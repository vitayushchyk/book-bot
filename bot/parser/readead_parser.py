import logging
from typing import List
from urllib.parse import urljoin

from bot.core.config import settings
from bot.parser.base_parser import BaseParser


class ReadeatParser(BaseParser):
    def __init__(self, base_url):
        super().__init__(base_url=base_url, api_url=settings.search_api_url_readeat)

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = await self.build_search_url(query=query)
        try:
            if not (res_text := await self.fetch_page(search_url)):
                return []

            data = await self._parse_json(res_text)
        except Exception as e:
            logging.error(
                f"[ Readeat Parser] An error occurred during data fetching: {e}"
            )
            return []

        books = self._parse_books(data.get("products", []))
        logging.info(f"[ Readeat Parser] Successfully parsed {len(books)}")
        for book in books:
            logging.info(f"[ Readeat Parser] Fetched {book}")
        return books

    def _parse_books(self, products: list) -> List[dict]:
        books = []
        for product in products:
            if isinstance(product, dict):
                self._add_book(product, books)
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
