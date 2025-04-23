import logging

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.base.base_shop import BaseShop
from bot.parser.bookling_parser import BooklingBookParser
from bot.services.bookling_processor import BookDetailsAdder, BookFilterAndSorter

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

        fetcher = BooklingBookParser(self.baseurl, PARSING_SETTINGS["bookling"])
        html_content = await fetcher.fetch_books_html(self.fetch_page, query)
        if not html_content:
            logging.error(f"Failed to fetch books for query: {query}")
            return []
        books = fetcher.parse_books_from_html(html_content)

        details_adder = BookDetailsAdder()
        detailed_books = await details_adder.add_details_to_books(books)

        filter_and_sorter = BookFilterAndSorter()
        processed_books = await filter_and_sorter.filter_and_sort_books(
            detailed_books, query
        )

        return processed_books
