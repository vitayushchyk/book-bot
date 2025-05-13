import logging

from bot.base.base_shop import BaseShop
from bot.parser.old_lion_parser import OldLionParser
from bot.processor.old_lion_processor import OldLionProcessor


class OldLion(BaseShop):
    async def get_book(self, query: str) -> list:
        if not query.strip():
            logging.warning("[Old Lion Store] Empty query provided.")
            return []

        parser = OldLionParser(base_url=self.baseurl)

        try:
            books_data = await parser.fetch_books_data(query)
            if not books_data:
                logging.warning("[Old Lion Store] No books were fetched.")
                return []

            processor = OldLionProcessor()
            detailed_books = await processor.add_details_to_books(books_data)
            logging.info(
                f"[Old Lion Store] Books after adding details: {len(detailed_books)}"
            )

            processed_books = await processor.filter_and_sort_books(
                detailed_books, query
            )
            logging.info(
                f"[Old Lion Store] Successfully fetched {len(processed_books)} books."
            )
            return processed_books

        except Exception as e:
            logging.error(f"[Old Lion Store] An error occurred: {e}")
            return []
