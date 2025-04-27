import logging
from typing import List

from bs4 import BeautifulSoup

PARSING_SETTINGS = {
    "yakaboo": {
        "book_container": "div.category-card",
        "title": "a.ui-card-title.category-card__name",
        "price": "div.category-card__content .category-card__price",
        "url": "a.category-card__image",
    }
}


class YakabooBookParser:
    def __init__(self, baseurl: str):
        self.baseurl = baseurl
        self.settings = PARSING_SETTINGS["yakaboo"]

    async def fetch_books_html(self, fetch_page, query: str) -> str:
        search_url = f"{self.baseurl}/search?q={query.strip()}"
        logging.info(f"Fetching Yakaboo books from URL: {search_url}")
        return await fetch_page(search_url)

    async def parse_books_from_html(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, features="html.parser")
        book_elements = soup.select(self.settings["book_container"])
        logging.info(f"Found {len(book_elements)} books on Yakaboo.")

        results = []
        for index, book_element in enumerate(book_elements):
            try:

                title_tag = book_element.select_one(self.settings["title"])
                title = title_tag.text.strip() if title_tag else None

                price_tag = book_element.select_one(self.settings["price"])
                price = price_tag.text.strip() if price_tag else None

                url_tag = book_element.select_one(self.settings["url"])
                url = f"{self.baseurl}{url_tag['href']}" if url_tag else None

                if not title or not url:
                    logging.warning(
                        f"Skipping book with missing data (title or URL): {index + 1}"
                    )
                    continue

                results.append({"title": title, "price": price, "url": url})
                logging.info(f"Book parsed: {title} ({price}) - {url}")

            except Exception as e:
                logging.error(f"Error parsing book element {index + 1}: {e}")

        return results
