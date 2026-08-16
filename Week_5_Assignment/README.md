# The Polite Scraper

A responsible web scraper built in Python for the FlyRank AI Week 5 Assignment A9 — "The Polite Scraper".

The project scrapes the public Books to Scrape practice sandbox, processes the first three catalogue pages, discovers 60 unique books, extracts their details, validates and normalizes the records, handles failures, and produces JSON evidence.

---

## Target Classification

### Target

Books to Scrape

https://books.toscrape.com/

### Why This Site

Books to Scrape is a public practice sandbox created specifically for learning and practising web scraping.

### Scope

This scraper processes only the first three catalogue pages.

The scraper discovers the book links from those three catalogue pages and processes the resulting 60 unique book detail pages.

### Robots Check

The URL:

https://books.toscrape.com/robots.txt

returns HTTP 404 Not Found.

No robots file was found.

### Responsible Scraping

I will not reuse this code on another site without checking its rules and terms first.

---

## Data Collected

Each book record contains:

- title
- product_url
- price_text
- price_gbp
- availability_text
- rating_text
- description
- source_page
- fetched_at

The original price text is preserved alongside the normalized numeric `price_gbp` value.

---

## Scraping Behaviour

The scraper uses:

- Requests for HTTP requests
- Beautiful Soup for HTML parsing
- Pydantic for schema validation
- Python JSON for output
- A descriptive User-Agent
- A request timeout
- Local HTML caching
- A minimum 500 ms delay between real requests
- One retry for timeouts and 5xx responses
- No retry for 403 or 404 responses

Cached pages are reused on subsequent runs to avoid unnecessary network requests.

---

## Project Stages

### Stage 0 — Classify Scraping Target

The target was classified as the Books to Scrape practice sandbox.

The first three catalogue pages were selected as the scraping scope.

### Stage 1 — Fetch Once, Cache Once

The first catalogue page is fetched using Requests and saved locally.

Subsequent runs reuse the cached HTML instead of downloading the page again.

### Stage 2 — Discover Three Catalogue Pages

The scraper follows the site's own pagination links and discovers exactly three catalogue pages.

Book links are converted to absolute URLs using `urljoin()`.

The result is:

- 3 catalogue pages
- 60 discovered book URLs
- 60 unique book URLs

### Stage 3 — Extract Book Details

The scraper visits the 60 unique book detail pages and extracts:

- title
- product_url
- price_text
- availability_text
- rating_text
- description
- source_page
- fetched_at

Missing descriptions are represented as `null`.

### Stage 4 — Validate Normalized Records

The raw records are normalized and validated using Pydantic.

The raw price is preserved and converted into a numeric `price_gbp` value.

The canonical identity of each book is its absolute `product_url`.

Valid records are written to:

`output/books.json`

Invalid records are written to:

`output/errors.json`

### Stage 5 — Survive Failures and Report the Run

The scraper handles individual page failures without stopping the entire run.

Timeouts and 5xx responses are retried once.

403 and 404 responses are not retried.

Each run produces:

`output/run-report.json`

The report records:

- start time
- duration
- pages fetched
- cache hits
- valid records
- invalid records
- failed pages

A deliberate fake URL was used during testing to confirm that a failed page does not prevent the remaining 60 valid records from being produced.

---

## Output Files

### `output/books.json`

Contains the 60 validated and normalized book records.

### `output/errors.json`

Contains records or pages that failed validation or fetching.

### `output/run-report.json`

Contains statistics about the scraper run.

### Sample 'run-report.json'

{
  "start_time": "2026-08-16T14:49:09.824439Z",
  "duration_seconds": 0.661,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}

---

## API / Scraper Results

| Result | Expected |
|---|---:|
| Catalogue pages | 3 |
| Discovered books | 60 |
| Unique book URLs | 60 |
| Detail pages | 60 |
| Valid records | 60 |

---

## Setup

### 1. Clone the Repository

Clone this repository and enter the `scraper` directory.

### 2. Install Dependencies

Install the packages listed in `requirements.txt`.

### 3. Run the Scraper

Run:

`python src/main.py`

The scraper will create the required output files automatically.