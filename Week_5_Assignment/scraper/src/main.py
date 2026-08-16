import os
import requests


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")

HEADERS = {
    "User-Agent": "FlyRankAI-PoliteScraper/1.0"
}


def fetch_catalogue_page():
    # Check whether cached HTML already exists
    if os.path.exists(CACHE_FILE):
        print("CACHE HIT")
        
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            return file.read()

    print("FETCH")

    # Create cache directory if it does not exist
    os.makedirs(CACHE_DIR, exist_ok=True)

    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        timeout=10
    )

    # Raise an error for HTTP errors
    response.raise_for_status()

    # Save HTML to cache
    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        file.write(response.text)

    return response.text


def main():
    html = fetch_catalogue_page()

    print(f"HTML length: {len(html)}")


if __name__ == "__main__":
    main()