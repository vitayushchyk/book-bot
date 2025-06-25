import logging
from typing import List

from bs4 import BeautifulSoup

from bot.core.config import settings
from bot.parser.base_parser import BaseParser


class MegogoBooksParser(BaseParser):
    BOOK_CONTAINER = ".product-wrapper"
    TITLE_ELEMENT = "a"
    PRICE_ELEMENT = '[data-testid="currentPrice"]'
    URL_ELEMENT = "a"
    URL_ATTRIBUTE = "href"
    BASE_URL = settings.base_url_mbooks

    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

    async def fetch_books_data(self, search_url) -> List[dict]:
        search_url = await self.build_search_url(search_url)
        logging.info(f"[Megogo Parser] Fetching data from URL: {search_url}")
        html_text = await self.fetch_page(search_url)
        if not html_text:
            return []

        soup = await self.parse_html_use_soup(html_text)
        pars_data = await self._parse_books(soup)
        logging.info(f"[Megogo Parser] Fetched {len(pars_data)}")
        for book in pars_data:
            logging.info(f"[Megogo Parser] Book: {book}")
        return pars_data

    async def _parse_books(self, soup: BeautifulSoup) -> List[dict]:
        books = []
        for book in soup.select(self.BOOK_CONTAINER):
            try:

                title_elm = book.select_one(self.TITLE_ELEMENT)
                title = title_elm.text.strip() if title_elm else None
                price_elm = book.select_one(self.PRICE_ELEMENT) or book.select_one(
                    self.PRICE_ELEMENT
                )
                price = price_elm.text.strip()

                url_elm = book.select_one(self.URL_ELEMENT)
                relative_url = url_elm.get(self.URL_ATTRIBUTE) if url_elm else None
                full_url = f"{self.BASE_URL}{relative_url}"
                if not title or not price or not full_url:
                    logging.warning(
                        f"[Megogo Parser] Skipped a card due to missing data: {title}, {price}, {full_url}"
                    )
                    continue

                books.append({"title": title, "price": price, "url": full_url})
            except AttributeError as e:
                logging.warning(
                    f"[Megogo Parser] Skipped a card due to an AttributeError: {str(e)}"
                )
                continue
        return books
