import asyncio
import logging
from typing import List

from bot.book_shop.base_shop import BaseShop


class BookSearchManager:
    def __init__(self, shops: List[BaseShop]):
        self.shops = shops

    async def fetch_books_from_all_libraries(self, book_name: str) -> List[dict]:
        tasks = [shop.get_book(book_name) for shop in self.shops]

        all_books = []
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for shop, result in zip(self.shops, results):
                if isinstance(result, Exception):
                    logging.error(
                        f"Error fetching data from {shop.__class__.__name__}: {result}"
                    )
                else:
                    logging.info(f"Found books in {shop.__class__.__name__}.")
                    all_books.extend(result)

        except Exception as overall_exception:
            logging.error(
                f"Unexpected error in book search manager: {overall_exception}"
            )
        return all_books
