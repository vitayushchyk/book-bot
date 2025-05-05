import logging
from typing import List

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class YakabooParser(FetchPageMixin, BaseParser):
    def __init__(self, base_url):
        self.base_url = base_url

    BOOK_CONTAINER = "div.category-card"
    TITLE_SELECTOR = "a.ui-card-title.category-card__name"
    PRICE_SELECTOR = "div.category-card__content .category-card__price"
    SPECIAL_PRICE_SELECTOR = ".special-price span"
    URL_SELECTOR = "a.category-card__image"
    URL_ATTRIBUTE = "href"

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        logging.info(f"[Yakaboo Parser] Fetching data from URL: {search_url}.")

        html_text = await self.fetch_page(search_url)
        if not html_text:
            return []

        soup = BeautifulSoup(html_text, features="html.parser")
        books = await self._parse_books(soup)
        logging.info(
            f"[Yakaboo Parser] Successfully fetched {len(books)} books from URL: {search_url}."
        )
        return books

    async def _parse_books(self, soup: BeautifulSoup) -> list:
        books = []

        for book in soup.select(self.BOOK_CONTAINER):
            try:

                title = await self._extract_text(
                    element=book, selector=self.TITLE_SELECTOR
                )

                price = await self._extract_text(
                    element=book, selector=self.SPECIAL_PRICE_SELECTOR
                ) or await self._extract_text(
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
                logging.warning("[Yakaboo Parser] Skipped a card due to missing data.")
                continue

        return books
