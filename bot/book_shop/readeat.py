import logging

from bot.base.base_shop import BaseShop
from bot.core.config import settings
from bot.parser.readead_parser import ReadeatParser
from bot.processor.readead_processor import ReadeatBookProcessor


class Readeat(BaseShop):
    async def get_book(self, query: str):
        if not query.strip():
            logging.warning("Empty query provided!")
            return []
        parser = ReadeatParser(base_url=settings.search_url_readeat)

        try:

            books = await parser.fetch_books_data(query)

            if not books:
                logging.warning("No books found after parsing.")
                return []

            processor = ReadeatBookProcessor()
            detailed_books = await processor.add_details_to_books(books)
            processed_books = await processor.filter_and_sort_books(
                detailed_books, query
            )

            return processed_books

        except Exception as e:
            logging.error(f"Unexpected error in Readeat parser: {e}")
            return []
