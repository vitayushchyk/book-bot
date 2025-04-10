import logging

import requests

from bot.book_shop.base_shop import BaseShop
from bot.core.config import settings


class EKnygarnya(BaseShop):
    async def get_book(self, book_name):

        search_url = f"{settings.search_url_eknygarnya}{book_name}&s=large"

        try:

            response = requests.get(search_url)
            response.raise_for_status()

            data = response.json()

            books = []

            item_groups = data.get("results", {}).get("item_groups", [])

            for group_index, group in enumerate(item_groups):
                for item_index, item in enumerate(group.get("items", [])):
                    try:

                        books.append(
                            {
                                "title": item.get("name", "Title not available"),
                                "price": item.get("price", "Price not available"),
                                "link": item.get("url", "#"),
                            }
                        )

                    except Exception as e:
                        logging.error(f"Error processing book: {e}")

                        continue

            return books

        except requests.RequestException as e:
            logging.error(f"API request error: {e}")

            return []
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

            return []
