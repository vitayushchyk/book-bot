import logging

from bot.base.base_shop import BaseShop
from bot.parser.yakaboo_parser import YakabooParser
from bot.processor.yakaboo_processor import YakabooProcessor


class Yakaboo(BaseShop):
    async def get_book(self, book_name: str) -> list:
        if not book_name.strip():
            logging.warning("Empty book name provided for Yakaboo.")
            return []

        parser = YakabooParser(self.baseurl)

        try:

            raw_books = await parser.fetch_books_data(book_name)
            if not raw_books:
                logging.warning("No books fetched from Yakaboo.")
                return []

            processor = YakabooProcessor()
            detailed_books = await processor.add_details_to_books(raw_books)
            final_books = await processor.filter_and_sort_books(
                detailed_books, book_name
            )

            logging.info(f"Successfully fetched {len(final_books)} books from Yakaboo.")
            return final_books

        except Exception as e:
            logging.error(f"An error occurred in Yakaboo: {e}")
            return []
