import logging

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.base.base_shop import BaseShop
from bot.utils.book_details import get_book_details
from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_price,
    sort_books_by_relevance,
)

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

        search_url = f"{self.baseurl}/catalog/?q={query.strip()}"
        logging.info(f"Searching books in Bookling with URL: {search_url}")

        get_html = await self.fetch_page(search_url)
        if not get_html:
            logging.error(f"Failed to fetch books from URL: {search_url}")
            return []

        soup = BeautifulSoup(get_html, features="html.parser")
        books = soup.select(PARSING_SETTINGS["bookling"]["book_container"])

        logging.info(f"Found {len(books)} book items in the HTML content.")

        results = []
        for book in books:

            get_title_element = book.select_one(PARSING_SETTINGS["bookling"]["title"])
            title = get_title_element.text.strip() if get_title_element else ""

            get_price_element = book.select_one(PARSING_SETTINGS["bookling"]["price"])
            price = f"{get_price_element.text.strip()}" if get_price_element else ""

            get_url_element = book.select_one(PARSING_SETTINGS["bookling"]["url"])
            url = f"{self.baseurl}{get_url_element['href']}" if get_url_element else ""

            if not title or not price or not url:
                logging.warning(f"Skipping book with missing data: {book}")
                continue

            book_data = {"title": title, "price": price, "url": url}

            detailed_book = await get_book_details(book_data, source_type="bookling")
            if detailed_book:
                results.append(detailed_book)

        logging.info(f"Total books after gathering details: {len(results)}")

        filtered_books = await filter_books_by_exact_match(results, query)

        if not filtered_books:
            filtered_books = await filter_books_by_similarity(results, query)

        logging.info(f"Books after filtering: {len(filtered_books)}")

        sorted_books = await sort_books_by_relevance(filtered_books, query)
        sorted_books = await sort_books_by_price(sorted_books)

        logging.info(f"Books after sorting: {len(sorted_books)}")

        return sorted_books
