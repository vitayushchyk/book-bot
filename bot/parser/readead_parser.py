import logging
from typing import List

from bs4 import BeautifulSoup

PARSING_SETTINGS = {
    "readeat": {
        "book_container": "div.fn_product.card.product-card",
        "title": {"key": "data-name"},
        "price": {"key": "data-price"},
        "url": "a.d-block",
    }
}


class ReadeatBookParser:
    def __init__(self, baseurl: str):
        self.baseurl = baseurl
        self.settings = PARSING_SETTINGS["readeat"]

    async def fetch_books_html(self, fetch_page, query: str) -> str:
        search_url = f"{self.baseurl}{query.strip()}"
        logging.info(f"Fetching books from URL: {search_url}")
        return await fetch_page(search_url)

    async def parse_books_from_html(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, features="html.parser")
        books_elements = soup.select(self.settings["book_container"])
        logging.info(f"Found {len(books_elements)} books on the page.")

        results = []
        for index, book_element in enumerate(books_elements, start=1):
            try:
                title = book_element.get(
                    self.settings["title"]["key"], "Title not available"
                ).strip()
                price = f"{book_element.get(self.settings['price']['key'], 'Price not available')} грн"
                url = (
                    book_element.select_one(self.settings["url"])["href"]
                    if book_element.select_one(self.settings["url"])
                    else "URL not available"
                )

                if not title or not price or not url:
                    logging.warning(f"Skipping book with missing data: {index}")
                    continue

                results.append({"title": title, "price": price, "url": url})
                logging.info(f"Book parsed: {title} ({price}) - {url}")

            except Exception as e:
                logging.error(f"Error parsing book {index}: {e}")

        return results
