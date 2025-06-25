import logging
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from bot.parser.base_parser import BaseParser


class BooklingParser(BaseParser):
    BOOK_CONTAINER = ".item_info.TYPE_1"
    TITLE_SELECTOR = ".item-title a span"
    PRICE_SELECTOR = ".price .price_value"
    URL_SELECTOR = ".item-title a"
    URL_ATTRIBUTE = "href"
    IN_STOCK_SELECTOR = ".item-stock .value"
    NOT_AVAILABLE_STATUS = "Немає в наявності"

    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

    async def fetch_books_data(self, search_url) -> List[dict]:
        search_url = await self.build_search_url(search_url)
        html_text = await self.fetch_page(search_url)
        if not html_text:
            return []

        soup = await self.parse_html_use_soup(html_text)
        pars_data = await self._parse_books(soup)

        logging.info(f"[Bookling Parser] Fetched {len(pars_data)}")
        for book in pars_data:
            logging.info(f"[Bookling Parser] Book: {book}")
        return pars_data

    async def _parse_books(self, soup: BeautifulSoup) -> List[dict]:
        books = []

        for book in soup.select(self.BOOK_CONTAINER):
            try:
                is_available_elm = book.select_one(self.IN_STOCK_SELECTOR)
                if is_available_elm:
                    is_available_text = is_available_elm.get_text(strip=True)
                    if self.NOT_AVAILABLE_STATUS in is_available_text:
                        logging.warning(
                            "[Bookling Parser] Skipping book as 'NOT AVAILABLE'"
                        )
                        continue
                title_elm = book.select_one(self.TITLE_SELECTOR)
                title = title_elm.get_text(strip=True) if title_elm else None
                price_elm = book.select_one(self.PRICE_SELECTOR)
                price = price_elm.get_text(strip=True) if price_elm else None
                url_elm = book.select_one(self.URL_SELECTOR)
                relative_url = url_elm[self.URL_ATTRIBUTE]
                url = urljoin(self.base_url, relative_url)

                if not title or not price or not url:
                    logging.warning(
                        f"[Bookling Parser] Skipped a card due to missing data: {title}, {price}, {url}"
                    )
                    continue

                books.append({"title": title, "price": price, "url": url})

            except AttributeError as e:
                logging.warning(
                    f"[Bookling Parser] Skipped a card due to an AttributeError: {str(e)}"
                )
                continue

        return books
