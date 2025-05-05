import logging

from bot.base.base_shop import BaseShop
from bot.core.config import settings
from bot.parser.zhupansky_parser import ZhupanskyParser
from bot.processor.zhupansky_processor import ZhupanskyProcessor


class ZhupanskyPublisher(BaseShop):
    async def get_book(self, query: str) -> list:
        if not query.strip():
            logging.warning("[Zhupansky Store] Empty query provided.")
            return []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        }

        parser = ZhupanskyParser(baseurl=settings.search_url_zhupansky, headers=headers)

        try:

            raw_books = parser.fetch_books_html(query)

            if not raw_books:
                logging.warning(f"[Zhupansky Store] No books were fetched.")
                return []

            for book in raw_books:
                book["price"] = parser.fetch_book_price(book["link"])

            processor = ZhupanskyProcessor()

            detailed_books = await processor.add_details_to_books(raw_books)
            logging.info(
                f"[Zhupansky Store] Books after adding details: {len(detailed_books)}"
            )

            logging.info(
                f"[Zhupansky Store] Filtering and sorting books: {len(detailed_books)}"
            )
            processed_books = await processor.filter_and_sort_books(
                detailed_books, query
            )

            logging.info(
                f"[Zhupansky Store] Successfully fetched {len(processed_books)} books for query '{query}'."
            )
            return processed_books

        except Exception as e:
            logging.error(f"[Zhupansky Store] Unexpected error: {e}", exc_info=True)
            return []
