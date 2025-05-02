import logging
from typing import List

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class ReadeatParser(FetchPageMixin, BaseParser):
    def __init__(self, base_url):
        self.base_url = base_url

    BOOK_CONTAINER = "div.fn_product.card.product-card"
    TITLE_ATTRIBUTE = "data-name"
    PRICE_ATTRIBUTE = "data-price"
    URL_SELECTOR = "a.d-block"
    URL_ATTRIBUTE = "href"

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        logging.info(f"Fetching data from URL: {search_url} in Readeat.")

        html_text = await self.fetch_page(search_url)
        if not html_text:
            return []

        soup = BeautifulSoup(html_text, features="html.parser")
        books = await self._parse_books(soup)
        logging.info(
            f"Successfully fetched {len(books)} books in Readeat from URL: {search_url}."
        )
        return books

    async def _parse_books(self, soup: BeautifulSoup) -> List[dict]:
        books = []

        for book in soup.select(self.BOOK_CONTAINER):
            try:

                title = book.get(self.TITLE_ATTRIBUTE)

                price = book.get(self.PRICE_ATTRIBUTE)

                url = await self._extract_attribute(
                    element=book,
                    selector=self.URL_SELECTOR,
                    attribute=self.URL_ATTRIBUTE,
                    base_url=self.base_url,
                )

                books.append({"title": title, "price": price, "url": url})

            except AttributeError:
                logging.warning("Skipped a card due to missing data in Readeat.")
                continue

        return books
