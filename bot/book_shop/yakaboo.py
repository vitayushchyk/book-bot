import logging

from bot.base.base_shop import BaseShop
from bot.parser.yakaboo_parser import YakabooParser
from bot.processor.yakaboo_processor import YakabooProcessor


class Yakaboo(BaseShop):
    async def get_book(self, book_name: str) -> list:
        if not book_name.strip():
            logging.warning("[Yakaboo Store] Empty query provided.")
            return []

        parser = YakabooParser(self.baseurl)

        try:

            raw_books = await parser.fetch_books_data(book_name)

            if not raw_books:
                logging.warning("[Yakaboo Store] No books were fetched.")
                return []

            processor = YakabooProcessor()

            detailed_books = await processor.add_details_to_books(raw_books)
            logging.info(
                f"[Yakaboo Store] Books after adding details: {len(detailed_books)}"
            )

            logging.info(
                f"[Yakaboo Store] Filtering and sorting books: {len(detailed_books)}"
            )
            final_books = await processor.filter_and_sort_books(
                detailed_books, book_name
            )

            logging.info(
                f"[Yakaboo Store] Successfully fetched {len(final_books)} books for query '{book_name}'."
            )
            return final_books

        except Exception as e:
            logging.error(f"[Yakaboo Store] An error occurred: {e}")
            return []
