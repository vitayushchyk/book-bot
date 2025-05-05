import logging
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from bot.parser.base_parser import BaseParser


class VivatParser(BaseParser):
    def __init__(
        self,
        base_url,
    ):
        self.base_url = base_url

    PRICE_SELECTOR = "meta[property='product:price:amount'][content]"

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        response = requests.get(search_url)

        if response.status_code != 200:
            logging.error(
                f"[Vivat Store] Request to URL {search_url} failed with status code {response.status_code}."
            )
            return []

        try:
            data = response.json()
        except Exception as e:
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
                if isinstance(item, list):
                    for sub_item in item:
                        if isinstance(sub_item, dict) and not sub_item.get(
                            "is_info_feed"
                        ):
                            books.append(
                                {
                                    "name": sub_item.get("name"),
                                    "url": sub_item.get("url"),
                                }
                            )
                elif isinstance(item, dict):
                    if not item.get("is_info_feed"):
                        books.append(
                            {
                                "name": item.get("name"),
                                "url": item.get("url"),
                            }
                        )

        logging.info(f"[Vivat Store] Found {len(books)} books for query '{query}'.")
        return books

    async def _get_book_price(self, book_url: str) -> Optional[dict]:
        response = requests.get(book_url)

        if response.status_code != 200:
            return {"price": "Price not found"}

        soup = BeautifulSoup(response.text, features="html.parser")

        price = soup.select_one(self.PRICE_SELECTOR)

        if price:
            price_content = price.get("content").strip()
            if price_content.replace(".", "").isdigit():
                logging.info(
                    f"[Vivat Store] Price successfully parsed: {price_content}"
                )
            else:
                logging.error(f"[Vivat Store] Invalid price format: {price_content}")
        else:
            logging.info("[Vivat Store] Price not found in HTML document.")

        return {
            "price": price.get("content") if price else "Price not found",
        }

    async def _parse_books(self, query: str) -> List[dict]:
        books = await self.fetch_books_data(query)
        results = []

        for book in books:
            price_data = await self._get_book_price(book["url"])
            logging.info(
                f"[Vivat Store] Parsed price for book '{book['name']}': {price_data}"
            )
            results.append(
                {
                    "title": book["name"],
                    "url": book["url"],
                    "price": price_data["price"],
                }
            )

        logging.info(
            f"[Vivat Store] Completed parsing {len(results)} books for query '{query}'."
        )
        return results
