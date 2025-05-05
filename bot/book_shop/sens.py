import logging

from bot.base.base_shop import BaseShop
from bot.parser.sens_parser import SensBookParser
from bot.processor.sens_processor import SensBookProcessor


class Sens(BaseShop):
    async def get_book(self, query: str) -> list:
        if not query.strip():
            logging.warning("[Sens Store] Empty query provided.")
            return []

        parser = SensBookParser(base_url=self.baseurl)

        try:
            books_data = await parser.fetch_books_data(query)
            if not books_data:
                logging.warning("[Sens Store] No books were fetched from Sens.")
                return []

            processor = SensBookProcessor()
            detailed_books = await processor.add_details_to_books(books_data)
            logging.info(
                f"[Sens Store] Books after adding details: {len(detailed_books)}"
            )
            processed_books = await processor.filter_and_sort_books(
                detailed_books, query
            )
            logging.info(
                f"[Sens Store] Books after filtering and sorting: {len(processed_books)}"
            )

            logging.info(
                f"[Sens Store] Successfully fetched {len(processed_books)} books."
            )
            return processed_books

        except Exception as e:
            logging.error(f"[Sens Store] An error occurred in Sens: {e}")
            return []
