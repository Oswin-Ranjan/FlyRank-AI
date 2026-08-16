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

[Write here exactly what you observed at https://books.toscrape.com/robots.txt]

### Responsible Scraping

Books to Scrape is a practice sandbox intended for scraping exercises, making it an appropriate target for this assignment.

I will not reuse this code on another site without checking its rules and terms first.