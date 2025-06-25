import logging
from typing import List

from bot.parser.base_parser import BaseParser


class KSDeKnygarnyaParser(BaseParser):
    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

    async def fetch_books_data(self, search_url) -> List[dict]:
        search_url = await self.build_search_url(search_url)
        try:
            await self.fetch_page(search_url)
            response_text = await self.fetch_page(search_url)
            if not response_text:
                return []
            data = await self._parse_json(response_text)
            item_groups = data.get("results", {}).get("item_groups", [])
        except Exception as e:
            logging.error(f"[KSD and EKnygarnya Parser] An error occurred: {e}")

            return []
        books = self._parse_books(item_groups)
        logging.info(f"[KSD and EKnygarnya Parser] Fetched {len(books)}")
        for book in books:
            logging.info(f"[KSD and EKnygarnya Parser] Fetched {book}")
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
