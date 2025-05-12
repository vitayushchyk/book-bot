import logging
from typing import List

import aiohttp

from bot.parser.base_parser import BaseParser


class KSDeKnygarnyaParser(BaseParser):
    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        logging.info(
            f"[KSD and EKnygarnya Parser] Fetching data from URL: {search_url}."
        )

        books = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status != 200:
                        logging.error(
                            f"[KSD and EKnygarnya Parser] Request to URL {search_url} failed with status code {response.status}."
                        )
                        return []

                    data = await response.json()

        except aiohttp.ClientError as e:
            logging.error(
                f"[KSD and EKnygarnya Parser] An error occurred while making the request: {e}"
            )
            return []

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
