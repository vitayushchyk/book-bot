import logging
from abc import ABC, abstractmethod


class BaseBManager(ABC):
    def __init__(
        self,
        baseurl: str,
    ):
        self.baseurl = baseurl

    @abstractmethod
    def get_parser(self):
        """Returns the parser for the shop"""
        pass

    @abstractmethod
    def get_processor(self):
        """Returns the processor for the shop"""
        pass

    async def get_book(self, query: str) -> list:
        """Main method for getting books from the shop."""
        if not query.strip():
            logging.warning(f"[{self.__class__.__name__}] Empty query.")
            return []

        parser = self.get_parser()
        processor = self.get_processor()

        try:
            raw_books = await parser.fetch_books_data(query)
            if not raw_books:
                logging.warning(f"[{self.__class__.__name__}] No books were fetched.")
                return []

            detailed_books = await processor.add_details_to_books(raw_books)
            logging.info(
                f"[{self.__class__.__name__}] Books after adding details: {len(detailed_books)}"
            )

            final_books = await processor.filter_and_sort_books(detailed_books, query)
            logging.info(
                f"[{self.__class__.__name__}] Successfully fetched {len(final_books)} books for query'{query}'."
            )

            return final_books

        except Exception as e:
            logging.error(f"[{self.__class__.__name__}] An error occurred: {e}")
            return []
