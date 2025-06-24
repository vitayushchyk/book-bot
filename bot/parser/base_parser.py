import json
import logging
from typing import Optional
from urllib.parse import urljoin


class BaseParser:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @staticmethod
    async def _parse_json(response_text: Optional[str]) -> Optional[dict]:
        """Parse the JSON response text."""
        if response_text is None:
            return None
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from response text.")
            return None

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
