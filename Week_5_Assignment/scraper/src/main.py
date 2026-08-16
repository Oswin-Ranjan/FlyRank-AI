import json
import os
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = "cache"
OUTPUT_DIR = "output"

HEADERS = {
    "User-Agent": "FlyRankAI-PoliteScraper/1.0"
}

REQUEST_DELAY = 0.5


class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str | None
    description: str | None
    source_page: HttpUrl
    fetched_at: str


def get_catalogue_cache_path(page_url):
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
    return os.path.join(
        CACHE_DIR,
        f"book-{index}.html"
    )


def fetch_page(url, cache_file):
    if os.path.exists(cache_file):
        print(f"CACHE HIT: {url}")

        with open(cache_file, "r", encoding="utf-8") as file:
            html = file.read()

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

    fetched_at = datetime.now(
        timezone.utc
    ).isoformat().replace("+00:00", "Z")

    return response.text, fetched_at, True


def discover_catalogue_pages():
    catalogue_pages = []
    book_entries = []

    current_url = BASE_URL

    while len(catalogue_pages) < 3:

        cache_file = get_catalogue_cache_path(
            current_url
        )

        html, _, was_fetched = fetch_page(
            current_url,
            cache_file
        )

        catalogue_pages.append(current_url)

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for article in soup.select(
            "article.product_pod"
        ):
            link = article.select_one(
                "h3 a"
            )

            if link and link.get("href"):
                product_url = urljoin(
                    current_url,
                    link["href"]
                )

                book_entries.append({
                    "product_url": product_url,
                    "source_page": current_url
                })

        if len(catalogue_pages) == 3:
            break

        next_link = soup.select_one(
            "li.next a"
        )

        if not next_link or not next_link.get("href"):
            break

        next_url = urljoin(
            current_url,
            next_link["href"]
        )

        if not os.path.exists(
            get_catalogue_cache_path(next_url)
        ):
            time.sleep(REQUEST_DELAY)

        current_url = next_url

    return catalogue_pages, book_entries


def extract_rating(soup):
    rating_element = soup.select_one(
        "p.star-rating"
    )

    if not rating_element:
        return None

    rating_names = {
        "One",
        "Two",
        "Three",
        "Four",
        "Five"
    }

    for class_name in rating_element.get(
        "class",
        []
    ):
        if class_name in rating_names:
            return class_name

    return None


def extract_description(soup):
    description_heading = soup.select_one(
        "#product_description"
    )

    if not description_heading:
        return None

    description = (
        description_heading.find_next_sibling("p")
    )

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
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    product_main = soup.select_one(
        "article.product_page"
    )

    if not product_main:
        product_main = soup

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

    rating_text = extract_rating(
        product_main
    )

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


def normalize_price(price_text):
    if not price_text:
        raise ValueError("Missing price_text")

    cleaned = (
        price_text
        .replace("Â£", "")
        .replace("£", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(
            f"Invalid price: {price_text}"
        )

def normalize_record(raw_record):
    price_gbp = normalize_price(
        raw_record["price_text"]
    )

    return {
        **raw_record,
        "price_gbp": price_gbp
    }


def extract_all_books(book_entries):
    raw_records = []

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

        if (
            was_fetched
            and index < len(book_entries)
        ):
            next_cache_file = get_detail_cache_path(
                index + 1
            )

            if not os.path.exists(next_cache_file):
                time.sleep(REQUEST_DELAY)

        raw_record = extract_book_record(
            html=html,
            product_url=product_url,
            source_page=source_page,
            fetched_at=fetched_at
        )

        raw_records.append(raw_record)

    return raw_records


def validate_and_store(raw_records):
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    valid_records = []
    errors = []
    seen_urls = set()

    for index, raw_record in enumerate(
        raw_records,
        start=1
    ):
        try:
            normalized = normalize_record(
                raw_record
            )

            record = BookRecord.model_validate(
                normalized
            )

            canonical_url = str(
                record.product_url
            )

            if canonical_url in seen_urls:
                errors.append({
                    "index": index,
                    "error": "Duplicate product_url",
                    "product_url": canonical_url
                })
                continue

            seen_urls.add(canonical_url)

            valid_records.append(
                record.model_dump(
                    mode="json"
                )
            )

        except (
            ValueError,
            ValidationError,
            TypeError,
            KeyError
        ) as error:

            errors.append({
                "index": index,
                "error": str(error),
                "record": raw_record
            })

    books_file = os.path.join(
        OUTPUT_DIR,
        "books.json"
    )

    errors_file = os.path.join(
        OUTPUT_DIR,
        "errors.json"
    )

    with open(
        books_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            valid_records,
            file,
            indent=2,
            ensure_ascii=False
        )

    with open(
        errors_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            errors,
            file,
            indent=2,
            ensure_ascii=False
        )

    return valid_records, errors


def main():
    catalogue_pages, book_entries = (
        discover_catalogue_pages()
    )

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

    raw_records = extract_all_books(
        unique_entries
    )

    print(
        f"detail_pages={len(raw_records)}"
    )

    valid_records, errors = validate_and_store(
        raw_records
    )

    print(
        f"valid_records={len(valid_records)}"
    )

    print(
        f"invalid_records={len(errors)}"
    )

    print(
        "books.json written to output/books.json"
    )

    print(
        "errors.json written to output/errors.json"
    )


if __name__ == "__main__":
    main()