# The Polite Scraper

## Target Classification

### Target

Books to Scrape

https://books.toscrape.com/

### Why This Site

Books to Scrape is a public practice sandbox created specifically for learning and practising web scraping.

### Scope

This assignment will process only the first three catalogue pages of Books to Scrape.

The scraper will discover the book links from those three catalogue pages and visit the resulting 60 unique book detail pages.

### Data Collected

For each book, the scraper will collect:

- title
- product_url
- price_text
- availability_text
- rating_text
- description
- source_page
- fetched_at

The normalized pipeline will also produce a numeric `price_gbp` value.

### Robots Check

Robots.txt result:

No robots file found. The URL `https://books.toscrape.com/robots.txt` returns HTTP 404 Not Found.

### Responsible Scraping

I will not reuse this code on another site without checking its rules and terms first.

---

## Stage 1 — Fetch Once, Cache Once

The scraper uses the Python `requests` library to fetch catalogue pages from Books to Scrape.

A descriptive User-Agent is sent with each request:

`FlyRankAI-PoliteScraper/1.0`

A request timeout is also configured to prevent the scraper from waiting indefinitely.

The first catalogue page is fetched from:

https://books.toscrape.com/

The downloaded HTML is stored locally at:

`cache/catalogue-page-1.html`

The cache is used to avoid making the same network request repeatedly.

### First Run

When the cache file does not exist, the scraper makes a network request and prints:

`FETCH`

The downloaded HTML is then saved to:

`cache/catalogue-page-1.html`

### Subsequent Runs

When the cached HTML already exists, the scraper does not make another network request.

Instead, it reads the existing HTML file and prints:

`CACHE HIT`

This keeps repeated development and testing runs polite by avoiding unnecessary requests to the target website.

---

## Stage 2 — Discover Three Catalogue Pages

The scraper parses the cached catalogue HTML using Beautiful Soup.

It starts from the Books to Scrape homepage and collects all book links from the first catalogue page.

Book links are converted from relative URLs to absolute URLs using Python's `urljoin()` rather than manually concatenating strings.

The scraper then follows the catalogue's own `Next` link to discover page 2 and then page 3.

The scraper stops after exactly three catalogue pages and does not hardcode the 60 book URLs.

A minimum delay of 500 milliseconds is used between real network requests. Cached pages do not require a delay because they do not contact the website.

Duplicate book URLs are removed before continuing to the next stage.

### Stage 2 Checkpoint

Expected output:

`catalogue_pages=3`

`discovered=60`

`unique_urls=60`

The same numbers should be produced when the scraper is run a second time, with the catalogue pages being read from cache.

---

## Stage 3 — Extract the Raw Records

The scraper now visits each of the 60 unique book detail pages discovered in Stage 2.

Each detail page is fetched using the same polite request rules:

- Identifying User-Agent
- 10-second request timeout
- HTTP status checking
- At least 500 ms between real requests
- Local HTML caching

The detail pages are cached under:

`cache/book-1.html` through `cache/book-60.html`

The scraper extracts the following eight raw fields from the product area:

- title
- product_url
- price_text
- availability_text
- rating_text
- description
- source_page
- fetched_at

The original text values are kept unchanged at this stage. Normalization and validation are handled in Stage 4.

If a description is missing, the value is stored as `null` rather than being invented.

The `source_page` field records which catalogue page contained the book link, while `fetched_at` records when the detail page was fetched.

### Stage 3 Checkpoint

Expected output:

`detail_pages=60`

The script also prints one complete raw record containing all eight required fields.

---

## Stage 4 — Validate Normalized Records

The raw records from Stage 3 are normalized and validated before being stored.

### Price Normalization

The raw `price_text` value is preserved and converted into a numeric `price_gbp` value.

For example:

`£51.77` → `51.77`

Both values are stored in the final record.

### Schema Validation

Pydantic is used to define and validate the final book record schema.

Each record contains:

- title
- product_url
- price_text
- price_gbp
- availability_text
- rating_text
- description
- source_page
- fetched_at

The `product_url` is used as the canonical identity of each book.

### Invalid Records

Records that fail normalization or schema validation are written to:

`output/errors.json`

Each error includes the reason and the associated record.

Invalid records are never added to `books.json`.

### Valid Records

Validated records are written to:

`output/books.json`

The output contains exactly 60 unique records.

### Idempotency

Running the scraper multiple times does not create duplicate records.

A second run continues to produce exactly 60 records because duplicate canonical product URLs are ignored.

### Stage 4 Checkpoint

Expected results:

- `books.json` contains exactly 60 records
- Every `price_gbp` value is numeric
- Every `product_url` starts with `https://`
- `errors.json` contains invalid records and their reasons
- Running the scraper again still produces exactly 60 records