import logging

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.base.base_shop import BaseShop
from bot.parser.bookling_parser import BooklingBookParser
from bot.processor.bookling_processor import BooklingProcessor

PARSING_SETTINGS = {
    "bookling": {
        "book_container": ".item_info.TYPE_1",
        "title": ".item-title a span",
        "price": ".price .price_value",
        "url": ".item-title a",
    }
}


class Bookling(BaseShop, FetchPageMixin):
    async def get_book(self, query: str):
        if not query.strip():
            logging.warning("Empty query provided!")
            return []

        bookling_parser = BooklingBookParser(self.baseurl, PARSING_SETTINGS["bookling"])
        html_content = await bookling_parser.fetch_books_html(self.fetch_page, query)

        if not html_content:
            logging.error(f"Failed to fetch books for query: {query}")
            return []

        raw_books = await bookling_parser.parse_books_from_html(html_content)

        processor = BooklingProcessor()
        detailed_books = await processor.add_details_to_books(raw_books)
        processed_books = await processor.filter_and_sort_books(detailed_books, query)

        return processed_books
