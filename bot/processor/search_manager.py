import asyncio
import json
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
        logging.info(f"[SEARCH] Start processing query: '{book_name}'")
        try:
            logging.info(f"[CACHE] Try to read cache for query: '{book_name}'")
            cached_books = await self.cache.get_cached_books(book_name)
            logging.info(f"[CACHE] redis.get('{book_name}') => {cached_books!r}")
            if cached_books:
                logging.info(f"[CACHE] Hit for '{book_name}', returning cached data")
                return cached_books
            else:
                logging.info(f"[CACHE] Miss for '{book_name}'")
        except Exception as e:
            logging.error(f"[CACHE] Error accessing cache for '{book_name}': {e}")

        async def limited_get_book(shop, book_name):
            try:
                logging.info(f"[API] Sending search to {shop.__class__.__name__}")
                res = await asyncio.wait_for(
                    shop.get_book(book_name), timeout=self.timeout
                )
                logging.info(f"[API] Result from {shop.__class__.__name__}: {res!r}")
                return res
            except asyncio.TimeoutError:
                logging.error(
                    f"[TIMEOUT] Timeout reached for shop {shop.__class__.__name__}"
                )
            except Exception as e:
                logging.error(
                    f"[SHOP] Error making request to {shop.__class__.__name__}: {e}"
                )
            return None

        tasks = [limited_get_book(shop, book_name) for shop in self.shops]
        all_books = []
        unavailable_shops = []

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for shop, result in zip(self.shops, results):
                if result is None:
                    logging.warning(
                        f"[RESULT] {shop.__class__.__name__}: None (error or no data)"
                    )
                    unavailable_shops.append(shop.__class__.__name__)
                elif isinstance(result, Exception):
                    logging.error(
                        f"[RESULT] Exception in {shop.__class__.__name__}: {result}"
                    )
                    unavailable_shops.append(shop.__class__.__name__)
                elif not isinstance(result, list):
                    logging.error(
                        f"[RESULT] Invalid response from {shop.__class__.__name__} (not a list): {result!r}"
                    )
                    unavailable_shops.append(shop.__class__.__name__)
                else:
                    logging.info(
                        f"[RESULT] Books found in {shop.__class__.__name__}: {len(result)} book(s)."
                    )
                    all_books.extend(result)

            if unavailable_shops:
                logging.warning(
                    f"[SHOP UNAVAILABLE] The following shops are unavailable: {', '.join(unavailable_shops)}"
                )

            if not all_books:
                logging.warning(f"[NO_BOOKS] No books found for query: '{book_name}'")

            if all_books:

                try:
                    logging.info(
                        f"[CACHE] Save {len(all_books)} results to cache for '{book_name}':\n{json.dumps(all_books, ensure_ascii=False, indent=2)}"
                    )

                    await self.cache.set_cached_books(book_name, all_books)
                except Exception as e:
                    logging.error(
                        f"[CACHE] Error saving data to cache for '{book_name}':\n{json.dumps(all_books, ensure_ascii=False, indent=2)} {e}"
                    )

        except Exception as overall_exception:
            logging.error(
                f"[FATAL] Unexpected error in BookSearchManager: {overall_exception}"
            )

        logging.info(f"[SEARCH] Finish processing query: '{book_name}'")
        return all_books
