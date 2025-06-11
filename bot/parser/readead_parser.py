import logging
from typing import List

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class ReadeatParser(FetchPageMixin, BaseParser):
    BOOK_CONTAINER = "div.fn_product.card.product-card"
    TITLE_ATTRIBUTE = "data-name"
    PRICE_ATTRIBUTE = "data-price"
    URL_SELECTOR = "a.d-block"
    URL_ATTRIBUTE = "href"
    AVALIABLE_BOOKS_SELECTOR = "div.notstock"

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        logging.info(f"[Readeat Parser] Fetching data from URL: {search_url}.")

        html_text = await self.fetch_page(search_url)
        if not html_text:
            return []

        soup = BeautifulSoup(html_text, features="html.parser")
        books = await self._parse_books(soup)
        logging.info(
            f"[Readeat Parser] Successfully fetched {len(books)} books from URL: {search_url}."
        )
        return books

    async def _parse_books(self, soup: BeautifulSoup) -> List[dict]:
        books = []

        for book in soup.select(self.BOOK_CONTAINER):
            try:

                not_in_stock = book.select_one(self.AVALIABLE_BOOKS_SELECTOR)
                if not_in_stock:
                    logging.info("[Readeat Parser] Book is not available, skipping.")
                    continue

                title = book.get(self.TITLE_ATTRIBUTE)
                price = book.get(self.PRICE_ATTRIBUTE)

                if not title or not price:
                    logging.warning(
                        "[Readeat Parser] Missing title or price, skipping."
                    )
                    continue

                url = await self._extract_attribute(
                    element=book,
                    selector=self.URL_SELECTOR,
                    attribute=self.URL_ATTRIBUTE,
                    base_url=self.base_url,
                )

                books.append({"title": title, "price": price, "url": url})

            except AttributeError as e:
                logging.warning(f"[Readeat Parser] Skipped a card due to error: {e}.")
                continue

        return books
