import logging

from bot.base.base_shop import BaseShop
from bot.parser.bookling_parser import BooklingParser
from bot.processor.bookling_processor import BooklingProcessor


class Bookling(BaseShop):
    async def get_book(self, book_name: str) -> list:
        if not book_name.strip():
            logging.warning("Empty book name provided for Yakaboo.")
            return []

        parser = BooklingParser(self.baseurl)

        try:

            raw_books = await parser.fetch_books_data(book_name)
            if not raw_books:
                logging.warning("No books fetched from Yakaboo.")
                return []

            processor = BooklingProcessor()
            detailed_books = await processor.add_details_to_books(raw_books)
            final_books = await processor.filter_and_sort_books(
                detailed_books, book_name
            )

            logging.info(f"Successfully fetched {len(final_books)} books from Yakaboo.")
            return final_books

        except Exception as e:
            logging.error(f"An error occurred in Yakaboo: {e}")
            return []
