import logging

from bot.base.base_shop import BaseShop
from bot.parser.sens_parser import SensBookParser
from bot.services.sens_processor import SensBookProcessor


class Sens(BaseShop):
    async def get_book(self, query: str) -> list:
        if not query.strip():
            logging.warning("Empty query provided for Sens.")
            return []

        parser = SensBookParser(self.driver, self.baseurl)

        try:

            books_data = await parser.fetch_books_data(query)
            if not books_data:
                logging.warning("No books were fetched from Sens.")
                return []

            processor = SensBookProcessor()
            detailed_books = await processor.add_details_to_books(books_data)
            processed_books = await processor.filter_and_sort_books(
                detailed_books, query
            )

            logging.info(f"Successfully fetched {len(processed_books)} books.")
            return processed_books

        except Exception as e:
            logging.error(f"An error occurred in Sens: {e}")
            return []
