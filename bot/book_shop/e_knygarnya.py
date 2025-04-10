import logging

import requests

from bot.book_shop.base_shop import BaseShop
from bot.core.config import settings
from bot.utils.book_details import get_book_details


class EKnygarnya(BaseShop):
    async def get_book(self, book_name):
        search_url = f"{settings.search_url_eknygarnya}{book_name}&s=large"

        try:
            logging.info(f"Fetching books from URL: {search_url}")

            response = requests.get(search_url)
            response.raise_for_status()

            data = response.json()

            books = []
            item_groups = data.get("results", {}).get("item_groups", [])

            for group in item_groups:
                for item in group.get("items", []):

                    try:
                        formatted_book = await get_book_details(
                            item, source_type="eknygarnya"
                        )
                        if formatted_book:
                            books.append(formatted_book)
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
