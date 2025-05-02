import logging
from typing import List

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class BooklingParser(FetchPageMixin, BaseParser):
    def __init__(self, base_url):
        self.base_url = base_url

    BOOK_CONTAINER = ".item_info.TYPE_1"
    TITLE_SELECTOR = ".item-title a span"
    PRICE_SELECTOR = ".price .price_value"
    URL_SELECTOR = ".item-title a"
    URL_ATTRIBUTE = "href"

    async def fetch_books_data(self, query: str) -> List[dict]:

        search_url = f"{self.base_url}{query.strip()}"
        logging.info(f"Fetching data from URL: {search_url} in Bookling.")

        html_text = await self.fetch_page(search_url)
        if not html_text:
            return []

        soup = BeautifulSoup(html_text, features="html.parser")
        books = await self._parse_books(soup)

        logging.info(
            f"Successfully fetched {len(books)} books in Bookling from URL: {search_url}."
        )
        return books

    async def _parse_books(self, soup: BeautifulSoup) -> List[dict]:
        books = []

        for book in soup.select(self.BOOK_CONTAINER):
            try:

                title = await self._extract_text(
                    element=book, selector=self.TITLE_SELECTOR
                )

                price = await self._extract_text(
                    element=book, selector=self.PRICE_SELECTOR
                )

                url = await self._extract_attribute(
                    element=book,
                    selector=self.URL_SELECTOR,
                    attribute=self.URL_ATTRIBUTE,
                    base_url=self.base_url,
                )

                books.append({"title": title, "price": price, "url": url})

            except AttributeError:
                logging.warning("Skipped a card due to missing data in Bookling.")
                continue

        return books
