import logging
from typing import List
from urllib.parse import urljoin

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.core.config import settings
from bot.parser.base_parser import BaseParser


class ReadeatParser(FetchPageMixin, BaseParser):
    def __init__(self, base_url):
        super().__init__(base_url=base_url)
        self.api_url = settings.search_api_url_readeat

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.api_url}{query.strip()}"
        logging.info(f"[ Readeat Parser] Fetching data from URL: {search_url}.")

        try:

            response_text = await self.fetch_page(search_url)

            if not response_text:
                logging.error(
                    f"[ Readeat Parser] Failed to fetch data from URL: {search_url}."
                )
                return []

            data = await self._parse_json(response_text)
        except Exception as e:
            logging.error(
                f"[ Readeat Parser] An error occurred during data fetching: {e}"
            )
            return []

        books = []

        products = data.get("products", [])
        for product in products:

            if isinstance(product, dict):
                self._add_book(product, books)

        logging.info(f"[ Readeat Parser] Parsed {len(books)} raw books from data.")
        return books

    @staticmethod
    def _add_book(item: dict, books: list):
        title = item.get("name")
        price = item.get("price")
        relative_url = item.get("link")
        full_url = urljoin(settings.base_url_readeat, relative_url)
        if title:
            books.append(
                {
                    "title": title,
                    "price": price,
                    "link": full_url,
                }
            )
