import logging

from bot.base.base_shop import BaseShop
from bot.parser.ksd_e_knygarnya_parser import KSDeKnygarnyaParser
from bot.processor.e_knygarnya_processor import E_Knygarnya_Processor


class EKnygarnya(BaseShop):
    async def get_book(self, query: str) -> list:
        if not query.strip():
            logging.warning("[EKnygarnya Store] Empty query provided.")
            return []

        parser = KSDeKnygarnyaParser(base_url=self.baseurl)

        try:
            detailed_books = await parser.fetch_books_data(query)
            if not detailed_books:
                logging.warning("[EKnygarnya Store] No books were fetched")
                return []

            processor = E_Knygarnya_Processor()
            detailed_books = await processor.add_details_to_books(detailed_books)
            logging.info(
                f"[EKnygarnya Store] Books after adding details: {len(detailed_books)}"
            )

            logging.info(
                f"[EKnygarnya Store] Filtering and sorting books: {len(detailed_books)}"
            )
            processed_books = await processor.filter_and_sort_books(
                detailed_books, query
            )
            logging.info(
                f"[EKnygarnya Store] Successfully fetched {len(processed_books)} books for query '{query}'."
            )
            return processed_books

        except Exception as e:
            logging.error(f"[EKnygarnya Store] An error occurred: {e}")
            return []
