import logging
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class YakabooParser(FetchPageMixin, BaseParser):

    BOOK_CONTAINER = "div.category-card"
    TITLE_SELECTOR = "a.ui-card-title.category-card__name"
    PRICE_SELECTOR = "div.category-card__content .category-card__price"
    NEW_PRICE_SELECTOR = ".special-price span"
    URL_SELECTOR = "a.category-card__image"
    URL_ATTRIBUTE = "href"

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        logging.info(f"[Yakaboo Parser] Fetching data from URL: {search_url}")

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

                title_elm = book.select_one(self.TITLE_SELECTOR)
                title = title_elm.get_text(strip=True) if title_elm else None

                is_special_price = book.select_one(self.NEW_PRICE_SELECTOR)
                price = (
                    is_special_price.get_text(strip=True) if is_special_price else None
                )
                if not price:
                    price_elm = book.select_one(self.PRICE_SELECTOR)
                    price = price_elm.get_text(strip=True) if price_elm else None

                url_element = book.select_one(self.URL_SELECTOR)
                url = (
                    urljoin(self.base_url, url_element[self.URL_ATTRIBUTE])
                    if url_element and self.URL_ATTRIBUTE in url_element.attrs
                    else None
                )

                if title and price and url:
                    books.append({"title": title, "price": price, "url": url})

            except AttributeError:
                logging.warning("[Yakaboo Parser] Skipped a card due to missing data.")
                continue

        return books
