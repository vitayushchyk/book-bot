import logging

from bot.base.base_shop import BaseShop
from bot.parser.vivat_parser import VivatParser
from bot.processor.vivat_processor import VivatProcessor


class Vivat(BaseShop):
    async def get_book(self, query: str) -> list:
        if not query.strip():
            logging.warning("Empty query provided for Vivat.")
            return []

        parser = VivatParser(base_url=self.baseurl)

        try:

            logging.info(f"Starting to parse books with query: {query.strip()}")
            detailed_books = await parser._parse_books(query)
            logging.info(f"Books fetched by parser: {detailed_books}")

            if not detailed_books:
                logging.warning("No books were fetched from Vivat.")
                return []

            processor = VivatProcessor()
            logging.info("Passing books to processor for additional details.")
            detailed_books = await processor.add_details_to_books(detailed_books)
            logging.info(f"Books after adding details: {detailed_books}")

            logging.info(f"Filtering and sorting books: {detailed_books}")
            processed_books = await processor.filter_and_sort_books(
                detailed_books, query
            )
            logging.info(f"Successfully fetched {len(processed_books)} books.")
            return processed_books

        except Exception as e:
            logging.error(f"An error occurred in Vivat: {e}")
            return []
