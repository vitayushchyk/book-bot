import logging

import requests

from bot.base.base_shop import BaseShop
from bot.utils.book_details import get_book_details
from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_relevance,
)


class Vivat(BaseShop):
    async def get_book(self, book_name):
        try:
            search_url = f"{self.baseurl}{book_name}"
            response = requests.get(search_url)
            response.raise_for_status()

            data = response.json()

            logging.info("Data successfully fetched.")
            books = []
            filter_titles = set()
            item_groups = data.get("results", {}).get("item_groups", [])

            for group in item_groups:
                for item_list in group.get("items", []):
                    if isinstance(item_list, list):
                        for item in item_list:
                            try:

                                formatted_book = await get_book_details(
                                    item, source_type="vivat"
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
            logging.error(f"Unexpected error while fetching books: {e}")
            return []
