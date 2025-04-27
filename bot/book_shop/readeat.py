import logging

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.base.base_shop import BaseShop
from bot.core.config import settings
from bot.parser.readeat_parser import ReadeatBookParser
from bot.services.readeat_processor import ReadeatBookProcessor


class Readeat(BaseShop, FetchPageMixin):
    async def get_book(self, query: str):
        if not query.strip():
            logging.warning("Empty query provided!")
            return []

        parser = ReadeatBookParser(baseurl=settings.search_url_readeat)

        try:
            html_content = await parser.fetch_books_html(self.fetch_page, query)
            if not html_content:
                logging.error("Failed to fetch books HTML content.")
                return []
            books = parser.parse_books_from_html(html_content)

            if not books:
                logging.warning("No books found after parsing.")
                return []

            processor = ReadeatBookProcessor()
            detailed_books = await processor.add_details_to_books(books)
            processed_books = await processor.filter_and_sort(detailed_books, query)

            return processed_books

        except Exception as e:
            logging.error(f"Unexpected error in Readeat parser: {e}")
            return []
