import logging
from typing import List

import requests

from bot.parser.base_parser import BaseParser


class KSDeKnygarnyaParser(BaseParser):
    def __init__(self, base_url):
        self.base_url = base_url

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        logging.info(
            f"[KSD and EKnygarnya Parser] Fetching data from URL: {search_url}."
        )

        books = []
        response = requests.get(search_url)

        if response.status_code != 200:
            logging.error(
                f"[KSD and EKnygarnya Parser] Request to URL {search_url} failed with status code {response.status_code}."
            )
            return []

        data = response.json()

        logging.info(f"API Response: {data}")

        item_groups = data.get("results", {}).get("item_groups", [])

        for group in item_groups:
            items = group.get("items", [])
            if not isinstance(items, list):
                logging.warning("Invalid format for items in group.")
                continue
            for item in items:

                title = item.get("name")
                if title:
                    logging.info(f"Book title: {title}")
                    books.append(
                        {
                            "title": title,
                            "price": item.get("price", "Price not available"),
                            "url": item.get("url", "#"),
                        }
                    )
                else:
                    logging.warning(f"Missing title in item: {item}")

        logging.info(f"Parsed {len(books)} raw books from data.")
        return books
