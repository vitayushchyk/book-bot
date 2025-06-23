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
            item_groups = data.get("results", {}).get("item_groups", [])
        except Exception as e:
            logging.error(
                f"[KSD and EKnygarnya Parser] An error occurred during data fetching: {e}"
            )
            return []

        books = self._parse_books(item_groups)
        logging.info(
            f"[KSD and EKnygarnya Parser] Successfully parsed {len(books)} books."
        )
        return books

    def _parse_books(self, item_groups: list) -> List[dict]:
        books = []
        for category_group in item_groups:
            book_items = category_group.get("items", [])
            if isinstance(book_items, list):
                for book_or_sublist in book_items:
                    if isinstance(book_or_sublist, dict):
                        if book_or_sublist.get("is_presence", True):
                            self._add_book(book_or_sublist, books)
                    elif isinstance(book_or_sublist, list):
                        for book_data in book_or_sublist:
                            if isinstance(book_data, dict):
                                if book_data.get("is_presence", True):
                                    self._add_book(book_data, books)
        return books
