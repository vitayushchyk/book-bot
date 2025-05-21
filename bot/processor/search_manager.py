import asyncio
import logging
from typing import List

from bot.manager.base_manager import BaseManager
from bot.utils.cache_manager import CacheManager


class BookSearchManager:
    def __init__(
        self,
        shops: List[BaseManager],
        max_concurrent_requests: int = 10,
        timeout: int = 30,
    ):
        self.shops = shops
        self.cache = CacheManager()
        self.max_concurrent_requests = max_concurrent_requests
        self.timeout = timeout

    async def fetch_books_from_all_libraries(self, book_name: str) -> List[dict]:
        try:

            cached_books = self.cache.get_cached_books(book_name)
            if cached_books:
                logging.info(f"Cache hit for query: '{book_name}'")
                return cached_books
        except Exception as e:
            logging.error(f"Error accessing cache: {e}")

        async def limited_get_book(shop, book_name):
            try:
                return await asyncio.wait_for(
                    shop.get_book(book_name), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                logging.error(f"Timeout reached for shop {shop.__class__.__name__}")
            except Exception as e:
                logging.error(f"Error making request to {shop.__class__.__name__}: {e}")
            return None

        tasks = [limited_get_book(shop, book_name) for shop in self.shops]
        all_books = []
        unavailable_shops = []

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for shop, result in zip(self.shops, results):
                if result is None:
                    unavailable_shops.append(shop.__class__.__name__)
                elif isinstance(result, Exception):
                    logging.error(
                        f"Exception occurred in {shop.__class__.__name__}: {result}"
                    )
                    unavailable_shops.append(shop.__class__.__name__)
                elif not isinstance(result, list):
                    logging.error(
                        f"Invalid response format from {shop.__class__.__name__} — expected a list."
                    )
                    unavailable_shops.append(shop.__class__.__name__)
                else:
                    logging.info(f"Books found in {shop.__class__.__name__}.")
                    all_books.extend(result)

            if unavailable_shops:
                logging.warning(
                    f"The following shops are unavailable: {', '.join(unavailable_shops)}"
                )

            if not all_books:
                logging.warning(f"No books found for query: '{book_name}'")

            if all_books:
                try:
                    self.cache.set_cached_books(book_name, all_books)
                except Exception as e:
                    logging.error(f"Error saving data to cache: {e}")

        except Exception as overall_exception:
            logging.error(f"Unexpected error: {overall_exception}")

        return all_books
