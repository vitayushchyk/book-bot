import logging
from typing import List

from bs4 import BeautifulSoup


class BooklingBookParser:
    def __init__(self, baseurl: str, parsing_settings: dict):
        self.baseurl = baseurl
        self.parsing_settings = parsing_settings

    async def fetch_books_html(self, fetch_page, query: str) -> str:
        search_url = f"{self.baseurl}/catalog/?q={query.strip()}"
        logging.info(f"Searching books with URL: {search_url}")
        return await fetch_page(search_url)

    def parse_books_from_html(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, features="html.parser")
        books = soup.select(self.parsing_settings["book_container"])

        results = []
        for book in books:
            title_element = book.select_one(self.parsing_settings["title"])
            price_element = book.select_one(self.parsing_settings["price"])
            url_element = book.select_one(self.parsing_settings["url"])

            title = title_element.text.strip() if title_element else ""
            price = price_element.text.strip() if price_element else ""
            url = f"{self.baseurl}{url_element['href']}" if url_element else ""

            if not title or not price or not url:
                logging.warning(f"Skipping book with missing data: {book}")
                continue

            results.append({"title": title, "price": price, "url": url})
            logging.info(price)
            logging.info(f"Book fetched: {title} ({price}) - {url}")

        return results
