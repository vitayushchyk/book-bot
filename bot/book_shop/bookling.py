import logging

from bot.base.base_shop import BaseShop
from bot.parser.bookling_parser import BooklingParser
from bot.processor.bookling_processor import BooklingProcessor


class Bookling(BaseShop):
    async def get_book(self, book_name: str) -> list:
        if not book_name.strip():
            logging.warning("[Bookling Store] Empty query provided.")
            return []

        parser = BooklingParser(self.baseurl)

        try:

            raw_books = await parser.fetch_books_data(book_name)

            if not raw_books:
                logging.warning("[Bookling Store] No books were fetched.")
                return []

            processor = BooklingProcessor()

            detailed_books = await processor.add_details_to_books(raw_books)
            logging.info(
                f"[Bookling Store] Books after adding details: {len(detailed_books)}"
            )

            logging.info(
                f"[Bookling Store] Filtering and sorting books: {len(detailed_books)}"
            )
            final_books = await processor.filter_and_sort_books(
                detailed_books, book_name
            )

            logging.info(
                f"[Bookling Store] Successfully fetched {len(final_books)} books for query '{book_name}'."
            )
            return final_books

        except Exception as e:
            logging.error(f"[Bookling Store] An error occurred: {e}")
            return []
