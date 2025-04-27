import logging

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.base.base_shop import BaseShop
from bot.parser.yakaboo_parser import YakabooBookParser
from bot.services.yakaboo_processor import YakabooBookProcessor


class Yakaboo(BaseShop, FetchPageMixin):
    async def get_book(self, query: str) -> list:
        if not query.strip():
            return []

        parser = YakabooBookParser(self.baseurl)

        try:

            html_content = await parser.fetch_books_html(self.fetch_page, query)
            if not html_content:
                logging.error("Failed to fetch Yakaboo HTML content.")
                return []

            books = await parser.parse_books_from_html(html_content)
            if not books:
                logging.warning(f"No books found for query '{query}' on Yakaboo.")
                return []

            processor = YakabooBookProcessor()
            detailed_books = await processor.add_details_to_books(books)
            processed_books = await processor.filter_and_sort_books(
                detailed_books, query
            )

            logging.info(
                f"Successfully fetched {len(processed_books)} books from Yakaboo."
            )
            return processed_books

        except Exception as e:
            logging.error(f"Unexpected error while processing Yakaboo books: {e}")
            return []
