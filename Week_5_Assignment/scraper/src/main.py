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
REQUEST_TIMEOUT = 10


class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str | None
    rating_text: str | None
    description: str | None
    source_page: HttpUrl
    fetched_at: str


class RunStats:
    def __init__(self):
        self.start_time = datetime.now(
            timezone.utc
        )

        self.pages_fetched = 0
        self.cache_hits = 0
        self.valid_records = 0
        self.invalid_records = 0
        self.failed_pages = 0

    def report(self):
        end_time = datetime.now(
            timezone.utc
        )

        duration = (
            end_time - self.start_time
        ).total_seconds()

        return {
            "start_time": self.start_time.isoformat().replace(
                "+00:00",
                "Z"
            ),
            "duration_seconds": round(
                duration,
                3
            ),
            "pages_fetched": self.pages_fetched,
            "cache_hits": self.cache_hits,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "failed_pages": self.failed_pages
        }


def get_catalogue_cache_path(page_url):
    if page_url == BASE_URL:
        return os.path.join(
            CACHE_DIR,
            "catalogue-page-1.html"
        )

    page_number = (
        page_url
        .rstrip("/")
        .split("page-")[-1]
    )

    return os.path.join(
        CACHE_DIR,
        f"catalogue-page-{page_number}.html"
    )


def get_detail_cache_path(index):
    return os.path.join(
        CACHE_DIR,
        f"book-{index}.html"
    )


def fetch_page(
    url,
    cache_file,
    stats,
    allow_retry=True
):
    """
    Fetch a page safely.

    Cache hit:
        Return cached HTML.

    Timeout / 5xx:
        Retry once.

    403 / 404:
        Do not retry.

    Other failures:
        Return failure information.
    """

    if os.path.exists(cache_file):
        stats.cache_hits += 1

        print(f"CACHE HIT: {url}")

        with open(
            cache_file,
            "r",
            encoding="utf-8"
        ) as file:
            html = file.read()

        fetched_at = datetime.fromtimestamp(
            os.path.getmtime(cache_file),
            tz=timezone.utc
        ).isoformat().replace(
            "+00:00",
            "Z"
        )

        return {
            "success": True,
            "html": html,
            "fetched_at": fetched_at,
            "was_fetched": False,
            "error": None
        }

    print(f"FETCH: {url}")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        stats.pages_fetched += 1

        # Successful response
        if response.status_code == 200:

            os.makedirs(
                CACHE_DIR,
                exist_ok=True
            )

            with open(
                cache_file,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(response.text)

            fetched_at = datetime.now(
                timezone.utc
            ).isoformat().replace(
                "+00:00",
                "Z"
            )

            return {
                "success": True,
                "html": response.text,
                "fetched_at": fetched_at,
                "was_fetched": True,
                "error": None
            }

        # 403 and 404 must NOT be retried
        if response.status_code in (403, 404):

            return {
                "success": False,
                "html": None,
                "fetched_at": None,
                "was_fetched": True,
                "error": (
                    f"HTTP {response.status_code}"
                )
            }

        # Retry server errors once
        if (
            500 <= response.status_code < 600
            and allow_retry
        ):
            print(
                f"HTTP {response.status_code} "
                f"for {url}. Retrying once..."
            )

            time.sleep(1)

            return fetch_page(
                url=url,
                cache_file=cache_file,
                stats=stats,
                allow_retry=False
            )

        return {
            "success": False,
            "html": None,
            "fetched_at": None,
            "was_fetched": True,
            "error": (
                f"HTTP {response.status_code}"
            )
        }

    except requests.Timeout:

        if allow_retry:
            print(
                f"Timeout for {url}. "
                f"Retrying once..."
            )

            time.sleep(1)

            return fetch_page(
                url=url,
                cache_file=cache_file,
                stats=stats,
                allow_retry=False
            )

        return {
            "success": False,
            "html": None,
            "fetched_at": None,
            "was_fetched": True,
            "error": "Request timeout"
        }

    except requests.RequestException as error:

        return {
            "success": False,
            "html": None,
            "fetched_at": None,
            "was_fetched": True,
            "error": str(error)
        }


def discover_catalogue_pages(stats):
    catalogue_pages = []
    book_entries = []

    current_url = BASE_URL

    while len(catalogue_pages) < 3:

        cache_file = get_catalogue_cache_path(
            current_url
        )

        result = fetch_page(
            current_url,
            cache_file,
            stats
        )

        if not result["success"]:
            print(
                f"Failed catalogue page: "
                f"{current_url}"
            )
            break

        catalogue_pages.append(
            current_url
        )

        soup = BeautifulSoup(
            result["html"],
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

        if (
            not next_link
            or not next_link.get("href")
        ):
            break

        next_url = urljoin(
            current_url,
            next_link["href"]
        )

        if not os.path.exists(
            get_catalogue_cache_path(
                next_url
            )
        ):
            time.sleep(
                REQUEST_DELAY
            )

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
        description_heading.find_next_sibling(
            "p"
        )
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

    availability_element = (
        product_main.select_one(
            "p.instock.availability"
        )
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
        raise ValueError(
            "Missing price_text"
        )

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
    return {
        **raw_record,
        "price_gbp": normalize_price(
            raw_record["price_text"]
        )
    }


def extract_all_books(
    book_entries,
    stats
):
    raw_records = []
    failures = []

    for index, book in enumerate(
        book_entries,
        start=1
    ):

        product_url = book[
            "product_url"
        ]

        source_page = book[
            "source_page"
        ]

        cache_file = get_detail_cache_path(
            index
        )

        result = fetch_page(
            product_url,
            cache_file,
            stats
        )

        if not result["success"]:

            stats.failed_pages += 1

            failure = {
                "index": index,
                "url": product_url,
                "error": result["error"]
            }

            failures.append(
                failure
            )

            print(
                f"FAILED: {product_url} "
                f"-> {result['error']}"
            )

            continue

        if (
            result["was_fetched"]
            and index < len(book_entries)
        ):
            next_cache_file = (
                get_detail_cache_path(
                    index + 1
                )
            )

            if not os.path.exists(
                next_cache_file
            ):
                time.sleep(
                    REQUEST_DELAY
                )

        try:

            raw_record = extract_book_record(
                html=result["html"],
                product_url=product_url,
                source_page=source_page,
                fetched_at=result["fetched_at"]
            )

            raw_records.append(
                raw_record
            )

        except Exception as error:

            stats.failed_pages += 1

            failures.append({
                "index": index,
                "url": product_url,
                "error": str(error)
            })

    return raw_records, failures


def validate_and_store(
    raw_records,
    failures,
    stats
):
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

                stats.invalid_records += 1

                continue

            seen_urls.add(
                canonical_url
            )

            valid_records.append(
                record.model_dump(
                    mode="json"
                )
            )

            stats.valid_records += 1

        except (
            ValueError,
            ValidationError,
            TypeError,
            KeyError
        ) as error:

            stats.invalid_records += 1

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

    # Include page-level failures in errors.json
    all_errors = failures + errors

    with open(
        errors_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_errors,
            file,
            indent=2,
            ensure_ascii=False
        )

    return valid_records, all_errors


def write_run_report(stats):
    report_file = os.path.join(
        OUTPUT_DIR,
        "run-report.json"
    )

    report = stats.report()

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )

    return report


def main():

    stats = RunStats()

    catalogue_pages, book_entries = (
        discover_catalogue_pages(
            stats
        )
    )

    unique_entries = []
    seen_urls = set()

    for book in book_entries:

        product_url = book[
            "product_url"
        ]

        if product_url not in seen_urls:

            seen_urls.add(
                product_url
            )

            unique_entries.append(
                book
            )       

    print(
        f"catalogue_pages="
        f"{len(catalogue_pages)}"
    )

    print(
        f"discovered="
        f"{len(book_entries)}"
    )

    print(
        f"unique_urls="
        f"{len(unique_entries)}"
    )

    raw_records, failures = (
        extract_all_books(
            unique_entries,
            stats
        )
    )

    print(
        f"detail_pages="
        f"{len(raw_records)}"
    )

    valid_records, errors = (
        validate_and_store(
            raw_records,
            failures,
            stats
        )
    )

    report = write_run_report(
        stats
    )

    print(
        f"valid_records="
        f"{len(valid_records)}"
    )

    print(
        f"invalid_records="
        f"{stats.invalid_records}"
    )

    print(
        f"failed_pages="
        f"{stats.failed_pages}"
    )

    print(
        "run-report.json written to "
        "output/run-report.json"
    )

    print(
        json.dumps(
            report,
            indent=2
        )
    )


if __name__ == "__main__":
    main()