import os
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = "cache"

HEADERS = {
    "User-Agent": "FlyRankAI-PoliteScraper/1.0"
}

REQUEST_DELAY = 0.5


def get_cache_path(page_url):
    if page_url == BASE_URL:
        return os.path.join(CACHE_DIR, "catalogue-page-1.html")

    page_number = page_url.rstrip("/").split("page-")[-1]
    return os.path.join(
        CACHE_DIR,
        f"catalogue-page-{page_number}.html"
    )


def fetch_page(page_url):
    cache_file = get_cache_path(page_url)

    # Use cached HTML if available
    if os.path.exists(cache_file):
        print(f"CACHE HIT: {page_url}")

        with open(cache_file, "r", encoding="utf-8") as file:
            return file.read()

    print(f"FETCH: {page_url}")

    os.makedirs(CACHE_DIR, exist_ok=True)

    response = requests.get(
        page_url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    with open(cache_file, "w", encoding="utf-8") as file:
        file.write(response.text)

    return response.text


def discover_catalogue_pages():
    catalogue_pages = []
    book_urls = []

    current_url = BASE_URL

    while len(catalogue_pages) < 3:
        html = fetch_page(current_url)

        catalogue_pages.append(current_url)

        soup = BeautifulSoup(html, "html.parser")

        # Find all book links on the current catalogue page
        for article in soup.select("article.product_pod"):
            link = article.select_one("h3 a")

            if link and link.get("href"):
                absolute_url = urljoin(current_url, link["href"])
                book_urls.append(absolute_url)

        # Stop after page 3
        if len(catalogue_pages) == 3:
            break

        # Follow the site's own "next" link
        next_link = soup.select_one("li.next a")

        if not next_link or not next_link.get("href"):
            break

        next_url = urljoin(current_url, next_link["href"])

        # Wait only before a real request.
        # Cached pages do not need a delay.
        if not os.path.exists(get_cache_path(next_url)):
            time.sleep(REQUEST_DELAY)

        current_url = next_url

    return catalogue_pages, book_urls


def main():
    catalogue_pages, book_urls = discover_catalogue_pages()

    # Remove duplicate URLs while preserving order
    unique_urls = list(dict.fromkeys(book_urls))

    print(f"catalogue_pages={len(catalogue_pages)}")
    print(f"discovered={len(book_urls)}")
    print(f"unique_urls={len(unique_urls)}")


if __name__ == "__main__":
    main()