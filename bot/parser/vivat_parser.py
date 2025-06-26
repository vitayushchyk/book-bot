import logging
from asyncio import gather
from typing import List, Optional

from bs4 import BeautifulSoup

from bot.parser.base_parser import BaseParser


class VivatParser(BaseParser):
    PRICE_SELECTOR = "meta[property='product:price:amount'][content]"

    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = await self.build_search_url(query=query)
        if not (res_text := await self.fetch_page(search_url)):
            return []

        try:
            data = await self._parse_json(res_text)
            if not data:
                return []
        except Exception as e:
            logging.error(f"[Vivat Store] An error occurred: {e}")
            return []

        results = data.get("results", {})
        if not isinstance(results, dict):
            return []

        item_groups = results.get("item_groups", [])
        if not isinstance(item_groups, list):
            return []

        books = await self._parse_books(item_groups)
        return books

    async def _parse_books(self, item_groups: list) -> List[dict]:
        books = []

        async def fetch_price(book_link: str) -> Optional[str]:
            try:
                response_text = await self.fetch_page(book_link)
                if not response_text:
                    return "Price not available"
                product_soup = BeautifulSoup(response_text, features="html.parser")
                price_meta = product_soup.select_one(self.PRICE_SELECTOR)
                if price_meta and price_meta.get("content"):
                    return f"{price_meta['content']} грн"
                return "Price not available"
            except Exception as e:
                logging.error(
                    msg="[Vivat Parser] Error fetching price for book: {e}",
                    exc_info=True,
                )
                return "Price not available"

        tasks = []
        for group in item_groups:
            if not isinstance(group, dict):
                continue

            items = group.get("items", [])
            if not isinstance(items, list):
                continue

            for item in items:
                if isinstance(item, list):
                    for sub_item in item:
                        if isinstance(sub_item, dict):

                            if not sub_item.get("is_presence", True):
                                logging.warning(
                                    f"[Vivat Parser] Skipping unavailable book: {sub_item.get('name', 'Unknown')}"
                                )
                                continue
                            book = {
                                "name": sub_item.get("name"),
                                "url": sub_item.get("url", "#"),
                            }
                            books.append(book)
                            tasks.append(fetch_price(book["url"]))

                elif isinstance(item, dict):
                    if not item.get("is_presence", True):
                        logging.info(
                            f"[Vivat Parser] Skipping unavailable book: {item.get('name', 'Unknown')}"
                        )
                        continue
                    book = {
                        "name": item.get("name"),
                        "url": item.get("url", "#"),
                    }
                    books.append(book)
                    tasks.append(fetch_price(book["url"]))

        books_prices = await gather(*tasks)
        for book, price in zip(books, books_prices):
            book["price"] = price

        return books
