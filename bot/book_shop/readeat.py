import logging

from bot.base.base_shop import BaseShop
from bot.core.config import settings
from bot.parser.readead_parser import ReadeatParser
from bot.processor.readead_processor import ReadeatBookProcessor


class Readeat(BaseShop):
    async def get_book(self, query: str):
        if not query.strip():
            logging.warning("[Readeat Store] Empty query provided!")
            return []
        parser = ReadeatParser(base_url=settings.search_url_readeat)

        try:

            books = await parser.fetch_books_data(query)

            if not books:
                logging.warning("[Readeat Store] No books found after parsing.")
                return []

            processor = ReadeatBookProcessor()

            detailed_books = await processor.add_details_to_books(books)
            logging.info(
                f"[Readeat Store] Books after adding details: {len(detailed_books)}"
            )

            logging.info(
                f"[Readeat Store] Filtering and sorting books: {len(detailed_books)}"
            )
            processed_books = await processor.filter_and_sort_books(
                detailed_books, query
            )
            logging.info(
                f"[Readeat Store] Successfully fetched {len(processed_books)} books for query '{query}'."
            )

            return processed_books

        except Exception as e:
            logging.error(f"[Readeat Store] Unexpected error: {e}")
            return []
