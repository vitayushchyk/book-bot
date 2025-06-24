import logging
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class SensBookParser(BaseParser, FetchPageMixin):

    BOOK_CONTAINER = "div.catalogCard-main"
    TITLE_PARENT_TAG = "div"
    TITLE_PARENT_CLASS = "catalogCard-title"
    TITLE_CHILD_TAG = "a"
    PRICE_PARENT_TAG = "div"
    PRICE_PARENT_CLASS = "catalogCard-price"
    LINK_TAG = "a"
    LINK_ATTRIBUTE = "href"
    LINK_PARENT_CLASS = "catalogCard-title"

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        logging.info(f"[Sens Parser] Fetching data from URL: {search_url}.")

        html_text = await self.fetch_page(search_url)
        if not html_text:
            return []

        soup = BeautifulSoup(html_text, features="html.parser")
        books = await self._parse_books(soup)
        logging.info(
            f"[Sens Parser] Successfully fetched {len(books)} books from URL: {search_url}."
        )
        return books

    async def _parse_books(self, soup: BeautifulSoup) -> List[dict]:
        books = []

        for card in soup.select(self.BOOK_CONTAINER):
            try:
                title_elm = card.find(
                    self.TITLE_PARENT_TAG, class_=self.TITLE_PARENT_CLASS
                )
                title = (
                    title_elm.find(self.TITLE_CHILD_TAG).get_text(strip=True)
                    if title_elm
                    else None
                )

                price_elm = card.find(
                    self.PRICE_PARENT_TAG, class_=self.PRICE_PARENT_CLASS
                )
                price = price_elm.get_text(strip=True) if price_elm else None

                link_parent = card.find(
                    self.TITLE_PARENT_TAG, class_=self.LINK_PARENT_CLASS
                )
                link_elm = link_parent.find(self.LINK_TAG) if link_parent else None
                link = (
                    urljoin(self.base_url, link_elm[self.LINK_ATTRIBUTE])
                    if link_elm
                    else None
                )

                if title and price and link:
                    books.append({"title": title, "price": price, "url": link})

            except AttributeError as e:
                logging.warning(
                    "[Sens Parser] SSkipped a card due to an AttributeError: {e}"
                )
                continue

        return books
