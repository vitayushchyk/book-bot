import asyncio
import logging
from typing import List

from bot.book_shop.base_shop import BaseShop
from bot.utils.cache_manager import CacheManager


class BookSearchManager:
    def __init__(self, shops: List[BaseShop], max_concurrent_requests: int = 5):
        self.shops = shops
        self.cache = CacheManager()
        self.max_concurrent_requests = max_concurrent_requests

    async def fetch_books_from_all_libraries(self, book_name: str) -> List[dict]:
        try:
            cached_books = self.cache.get_cached_books(book_name)
            if cached_books:
                logging.info(f"Received cached data for the query: '{book_name}'")
                return cached_books
        except Exception as e:
            logging.error(f"Error accessing cache: {e}")

        semaphore = asyncio.Semaphore(value=self.max_concurrent_requests)

        async def limited_get_book(shop, book_name):
            async with semaphore:
                return await shop.get_book(book_name)

        tasks = [limited_get_book(shop, book_name) for shop in self.shops]
        all_books = []

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for shop, result in zip(self.shops, results):
                if isinstance(result, Exception):
                    logging.error(
                        f"Error while fetching data from {shop.__class__.__name__}: {result}"
                    )
                elif not isinstance(result, list):
                    logging.error(
                        f"Invalid response format from {shop.__class__.__name__}"
                    )
                else:
                    logging.info(f"Books found in {shop.__class__.__name__}.")
                    all_books.extend(result)

            if not all_books:
                logging.warning(f"No books found for the query: '{book_name}'")

            try:
                self.cache.set_cached_books(book_name, all_books)
            except Exception as e:
                logging.error(f"Error saving data to cache: {e}")

        except Exception as overall_exception:
            logging.error(
                f"Unexpected error in the search manager: {overall_exception}"
            )

        return all_books
