import logging

from bot.base.base_shop import BaseShop
from bot.parser.ksd_e_knygarnya_parser import KSDeKnygarnyaParser
from bot.processor.ksd_processor import KSDProcessor


class KSD(BaseShop):
    async def get_book(self, query: str) -> list:
        if not query.strip():
            logging.warning("[KSD Store] Empty query provided.")
            return []

        parser = KSDeKnygarnyaParser(base_url=self.baseurl)

        try:
            detailed_books = await parser.fetch_books_data(query)
            if not detailed_books:
                logging.warning("[KSD Store] No books were fetched")
                return []

            processor = KSDProcessor()
            detailed_books = await processor.add_details_to_books(detailed_books)
            logging.info(
                f"[KSD Store] Books after adding details: {len(detailed_books)}"
            )

            logging.info(
                f"[KSD Store] Filtering and sorting books: {len(detailed_books)}"
            )
            processed_books = await processor.filter_and_sort_books(
                detailed_books, query
            )
            logging.info(
                f"[KSD Store] Successfully fetched {len(processed_books)} books for query '{query}'."
            )
            return processed_books

        except Exception as e:
            logging.error(f"[KSD Store] An error occurred: {e}")
            return []
