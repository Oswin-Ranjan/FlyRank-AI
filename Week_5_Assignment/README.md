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

### Cache Protection

The `cache/` directory is included in `.gitignore` so downloaded HTML is not committed to the repository.

---

## Project Structure

```text
scraper/
├── cache/
│   └── catalogue-page-1.html
├── src/
│   └── main.py
├── README.md
├── .gitignore
└── requirements.txt