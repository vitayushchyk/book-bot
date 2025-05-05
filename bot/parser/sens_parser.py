import logging
from typing import List

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class SensBookParser(BaseParser, FetchPageMixin):
    def __init__(self, base_url):
        self.base_url = base_url

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
                title = await self._extract_text(
                    card,
                    parent_tag=self.TITLE_PARENT_TAG,
                    parent_class=self.TITLE_PARENT_CLASS,
                    child_tag=self.TITLE_CHILD_TAG,
                )

                price = await self._extract_text(
                    card,
                    parent_tag=self.PRICE_PARENT_TAG,
                    parent_class=self.PRICE_PARENT_CLASS,
                )

                link = await self._extract_attribute(
                    card,
                    tag=self.LINK_TAG,
                    attribute=self.LINK_ATTRIBUTE,
                    parent_class=self.LINK_PARENT_CLASS,
                    base_url=self.base_url,
                )

                books.append({"title": title, "price": price, "url": link})

            except AttributeError:
                logging.warning("[Sens Parser] Skipped a card due to missing data.")
                continue

        return books
