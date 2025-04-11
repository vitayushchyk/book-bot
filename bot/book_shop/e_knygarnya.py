import logging

import requests

from bot.book_shop.base_shop import BaseShop
from bot.core.config import settings
from bot.utils.book_details import get_book_details
from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_relevance,
)


class EKnygarnya(BaseShop):
    async def get_book(self, book_name):
        search_url = f"{settings.search_url_eknygarnya}{book_name}&s=large"

        try:

            response = requests.get(search_url)
            response.raise_for_status()

            data = response.json()

            books = []
            filter_titles = set()
            item_groups = data.get("results", {}).get("item_groups", [])

            for group in item_groups:
                for item in group.get("items", []):
                    try:

                        formatted_book = await get_book_details(
                            item, source_type="eknygarnya"
                        )

                        if (
                            formatted_book
                            and formatted_book["title"] not in filter_titles
                        ):
                            books.append(formatted_book)
                            filter_titles.add(formatted_book["title"])
                        else:
                            logging.warning(
                                f"Skipping duplicate or incomplete book: {item.get('name', 'No title provided')}"
                            )

                    except Exception as e:
                        logging.error(f"Error processing book: {e}")
                        continue

            books = await filter_books_by_exact_match(books, book_name)

            if not books:
                books = await filter_books_by_similarity(books, book_name)

            books = await sort_books_by_relevance(books, book_name)

            return books

        except requests.RequestException as e:
            logging.error(f"API request error: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return []
