import logging
from asyncio import gather
from typing import List, Optional

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class VivatParser(BaseParser, FetchPageMixin):
    PRICE_SELECTOR = "meta[property='product:price:amount'][content]"

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        response_text = await self.fetch_page(search_url)

        if not response_text:
            logging.warning("[Vivat Store] No response received from server.")
            return []

        try:
            data = await self._parse_json(response_text)
            if not data:
                return []
        except Exception as e:
            logging.error(f"[Vivat Store] An error occurred: {e}")
            return []

        results = data.get("results", {})
        if not isinstance(results, dict):
            return []

        books = []
        item_groups = results.get("item_groups", [])
        if not isinstance(item_groups, list):
            return []

        for group in item_groups:
            if not isinstance(group, dict):
                continue

            items = group.get("items", [])
            if not isinstance(items, list):
                continue

            for item in items:
                # If items contain nested lists (e.g., [[{}]])

                if isinstance(item, list):
                    for sub_item in item:
                        if isinstance(sub_item, dict) and not sub_item.get(
                            "is_info_feed"
                        ):
                            books.append(
                                {
                                    "name": sub_item.get("name"),
                                    "url": sub_item.get("url", "#"),
                                }
                            )
                # If items contain a regular dictionary
                elif isinstance(item, dict):
                    if not item.get("is_info_feed"):
                        books.append(
                            {
                                "name": item.get("name"),
                                "url": item.get("url", "#"),
                            }
                        )

        books_prices = await gather(
            *[self._fetch_book_price(book["url"]) for book in books]
        )
        for book, price in zip(books, books_prices):
            book["price"] = price

        return books

    async def _fetch_book_price(self, book_link: str) -> Optional[str]:
        try:
            response_text = await self.fetch_page(book_link)
            logging.info(f"[Vivat Parser] Fetching price for book link: {book_link}")
            if not response_text:
                logging.warning(
                    f"[Vivat Parser] No response for book link: {book_link}"
                )
                return "Price not available"
            product_soup = BeautifulSoup(response_text, features="html.parser")
            price_meta = product_soup.select_one(self.PRICE_SELECTOR)
            if price_meta and price_meta.get("content"):
                return f"{price_meta['content']} грн"
            return "Price not available"
        except Exception as e:
            logging.error(
                f"[Vivat Parser] Error fetching price for book: {e}", exc_info=True
            )
            return "Price not available"
