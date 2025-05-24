import logging
from typing import List

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class KSDeKnygarnyaParser(BaseParser, FetchPageMixin):
    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        logging.info(
            f"[KSD and EKnygarnya Parser] Fetching data from URL: {search_url}."
        )

        try:

            response_text = await self.fetch_page(search_url)

            if not response_text:
                logging.error(
                    f"[KSD and EKnygarnya Parser] Failed to fetch data from URL: {search_url}."
                )
                return []

            data = await self._parse_json(response_text)
        except Exception as e:
            logging.error(
                f"[KSD and EKnygarnya Parser] An error occurred during data fetching: {e}"
            )
            return []

        books = []

        item_groups = data.get("results", {}).get("item_groups", [])
        for group in item_groups:
            items = group.get("items", [])
            if isinstance(items, list):
                for item_or_sublist in items:
                    if isinstance(item_or_sublist, dict):
                        self._add_book(item_or_sublist, books)
                    elif isinstance(item_or_sublist, list):
                        for item in item_or_sublist:
                            if isinstance(item, dict):
                                self._add_book(item, books)

        logging.info(
            f"[KSD and EKnygarnya Parser] Parsed {len(books)} raw books from data."
        )
        return books

    @staticmethod
    def _add_book(item: dict, books: list):
        title = item.get("name")
        price = item.get("price")
        url = item.get("url")
        if title:
            books.append(
                {
                    "title": title,
                    "price": price,
                    "url": url,
                }
            )
