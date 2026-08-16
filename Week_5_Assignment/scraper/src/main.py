import os
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = "cache"

HEADERS = {
    "User-Agent": "FlyRankAI-PoliteScraper/1.0"
}

REQUEST_DELAY = 0.5


def get_catalogue_cache_path(page_url):
    """
    Returns the cache filename for a catalogue page.
    """
    if page_url == BASE_URL:
        return os.path.join(
            CACHE_DIR,
            "catalogue-page-1.html"
        )

    page_number = page_url.rstrip("/").split("page-")[-1]

    return os.path.join(
        CACHE_DIR,
        f"catalogue-page-{page_number}.html"
    )


def get_detail_cache_path(index):
    """
    Returns the cache filename for a book detail page.
    """
    return os.path.join(
        CACHE_DIR,
        f"book-{index}.html"
    )


def fetch_page(url, cache_file):
    """
    Fetch a page from the website if it is not cached.
    Otherwise, read the cached HTML.
    """

    if os.path.exists(cache_file):
        print(f"CACHE HIT: {url}")

        with open(cache_file, "r", encoding="utf-8") as file:
            html = file.read()

        # Use the cache file modification time as the
        # original fetch timestamp when reading from cache.
        fetched_at = datetime.fromtimestamp(
            os.path.getmtime(cache_file),
            tz=timezone.utc
        ).isoformat().replace("+00:00", "Z")

        return html, fetched_at, False

    print(f"FETCH: {url}")

    os.makedirs(CACHE_DIR, exist_ok=True)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    with open(cache_file, "w", encoding="utf-8") as file:
        file.write(response.text)

    fetched_at = datetime.now(timezone.utc).isoformat().replace(
        "+00:00",
        "Z"
    )

    return response.text, fetched_at, True


def discover_catalogue_pages():
    """
    Discover the first three catalogue pages and
    all book URLs on those pages.

    Returns:
        catalogue_pages
        book_entries
    """

    catalogue_pages = []
    book_entries = []

    current_url = BASE_URL

    while len(catalogue_pages) < 3:

        cache_file = get_catalogue_cache_path(current_url)

        html, _, was_fetched = fetch_page(
            current_url,
            cache_file
        )

        catalogue_pages.append(current_url)

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # Find all books on the catalogue page
        for article in soup.select("article.product_pod"):

            link = article.select_one("h3 a")

            if link and link.get("href"):

                product_url = urljoin(
                    current_url,
                    link["href"]
                )

                book_entries.append({
                    "product_url": product_url,
                    "source_page": current_url
                })

        # Stop after exactly three catalogue pages
        if len(catalogue_pages) == 3:
            break

        # Follow the site's own Next link
        next_link = soup.select_one("li.next a")

        if not next_link or not next_link.get("href"):
            break

        next_url = urljoin(
            current_url,
            next_link["href"]
        )

        # Wait only before an actual network request
        if not os.path.exists(
            get_catalogue_cache_path(next_url)
        ):
            time.sleep(REQUEST_DELAY)

        current_url = next_url

    return catalogue_pages, book_entries


def extract_rating(soup):
    """
    Extract the rating text from the product's
    star-rating element.
    """

    rating_element = soup.select_one(
        "p.star-rating"
    )

    if not rating_element:
        return None

    classes = rating_element.get("class", [])

    rating_names = {
        "One",
        "Two",
        "Three",
        "Four",
        "Five"
    }

    for class_name in classes:
        if class_name in rating_names:
            return class_name

    return None


def extract_description(soup):
    """
    Extract the description from the product area.

    Returns None if the page does not contain
    a description.
    """

    description_heading = soup.select_one(
        "#product_description"
    )

    if not description_heading:
        return None

    description = description_heading.find_next_sibling("p")

    if not description:
        return None

    text = description.get_text(
        " ",
        strip=True
    )

    return text if text else None


def extract_book_record(
    html,
    product_url,
    source_page,
    fetched_at
):
    """
    Extract the eight raw fields required by Stage 3.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Product area only
    product_main = soup.select_one(
        "article.product_page"
    )

    if not product_main:
        product_main = soup

    # Title
    title_element = product_main.select_one(
        "h1"
    )

    title = (
        title_element.get_text(
            " ",
            strip=True
        )
        if title_element
        else None
    )

    # Price
    price_element = product_main.select_one(
        "p.price_color"
    )

    price_text = (
        price_element.get_text(
            " ",
            strip=True
        )
        if price_element
        else None
    )

    # Availability
    availability_element = product_main.select_one(
        "p.instock.availability"
    )

    availability_text = (
        availability_element.get_text(
            " ",
            strip=True
        )
        if availability_element
        else None
    )

    # Rating
    rating_text = extract_rating(
        product_main
    )

    # Description
    description = extract_description(
        product_main
    )

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }


def extract_all_books(book_entries):
    """
    Fetch, cache and extract all discovered book pages.
    """

    raw_records = []
    detail_pages = 0

    for index, book in enumerate(
        book_entries,
        start=1
    ):

        product_url = book["product_url"]
        source_page = book["source_page"]

        cache_file = get_detail_cache_path(
            index
        )

        html, fetched_at, was_fetched = fetch_page(
            product_url,
            cache_file
        )

        # Wait at least 500 ms before the next
        # real network request.
        if (
            was_fetched
            and index < len(book_entries)
        ):
            next_cache_file = get_detail_cache_path(
                index + 1
            )

            if not os.path.exists(next_cache_file):
                time.sleep(REQUEST_DELAY)

        record = extract_book_record(
            html=html,
            product_url=product_url,
            source_page=source_page,
            fetched_at=fetched_at
        )

        raw_records.append(record)
        detail_pages += 1

    return raw_records, detail_pages


def main():

    catalogue_pages, book_entries = (
        discover_catalogue_pages()
    )

    # Remove duplicate product URLs while
    # preserving the first source page.
    unique_entries = []
    seen_urls = set()

    for book in book_entries:

        product_url = book["product_url"]

        if product_url not in seen_urls:
            seen_urls.add(product_url)
            unique_entries.append(book)

    print(
        f"catalogue_pages={len(catalogue_pages)}"
    )

    print(
        f"discovered={len(book_entries)}"
    )

    print(
        f"unique_urls={len(unique_entries)}"
    )

    raw_records, detail_pages = extract_all_books(
        unique_entries
    )

    print(
        f"detail_pages={detail_pages}"
    )

    # Print exactly one complete raw record
    if raw_records:
        print("\nFirst raw record:")
        print(raw_records[0])


if __name__ == "__main__":
    main()