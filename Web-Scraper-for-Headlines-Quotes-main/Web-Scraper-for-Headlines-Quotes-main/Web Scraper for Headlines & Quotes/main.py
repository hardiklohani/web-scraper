
import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path

# Website URL
BASE_URL = "https://quotes.toscrape.com"
PAGE_URL = BASE_URL + "/page/{}/"

# HTML selectors
SELECTORS = {
    "quote": "div.quote",
    "text": "span.text",
    "author": "small.author",
    "tags": "div.tags a.tag"
}

OUTPUT_FILE = Path(__file__).parent / "quotes.json"

MAX_PAGES = 2
REQUEST_DELAY = 1


# Fetch webpage
def fetch_page(url):
    headers = {
        "User-Agent": "LearningProjectQuoteScraper/1.0"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()
        return response.text

    except requests.exceptions.RequestException as error:
        print("Error fetching webpage:", error)
        return None


# Extract quotes
def extract_quotes(html):

    soup = BeautifulSoup(html, "html.parser")

    records = []

    quote_elements = soup.select(SELECTORS["quote"])

    for item in quote_elements:

        text_element = item.select_one(SELECTORS["text"])
        author_element = item.select_one(SELECTORS["author"])

        # Check if elements exist
        if text_element is None or author_element is None:
            continue

        tag_elements = item.select(SELECTORS["tags"])

        quote_data = {
            "quote": text_element.get_text(strip=True).strip("“”"),
            "author": author_element.get_text(strip=True),
            "tags": [
                tag.get_text(strip=True)
                for tag in tag_elements
            ]
        }

        records.append(quote_data)

    return records


# Scrape multiple pages
def scrape_quotes():

    all_quotes = []

    for page_number in range(1, MAX_PAGES + 1):

        url = PAGE_URL.format(page_number)

        print("Fetching page:", page_number)

        html = fetch_page(url)

        if html is None:
            continue

        quotes = extract_quotes(html)

        all_quotes.extend(quotes)

        print("Quotes found:", len(quotes))

        if page_number < MAX_PAGES:
            time.sleep(REQUEST_DELAY)

    return all_quotes


# Save data into JSON file
def save_quotes(records):

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:

        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=4
        )


# Main function
def main():

    print("===== WEB SCRAPER FOR QUOTES =====")

    quotes = scrape_quotes()

    if not quotes:

        print("No quotes found.")
        return

    save_quotes(quotes)

    print("\nScraping completed successfully!")
    print("Total quotes extracted:", len(quotes))
    print("Data saved in quotes.json")


if __name__ == "__main__":
    main()
