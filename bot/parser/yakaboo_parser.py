import logging
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from bot.parser.base_parser import BaseParser


class YakabooParser(BaseParser):

    BOOK_CONTAINER = "div.category-card"
    TITLE_SELECTOR = "a.ui-card-title.category-card__name"
    PRICE_SELECTOR = "div.category-card__content .category-card__price"
    NEW_PRICE_SELECTOR = ".special-price span"
    URL_SELECTOR = "a.category-card__image"
    URL_ATTRIBUTE = "href"

    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = await self.build_search_url(query=query)

        if not (html_text := await self.fetch_page(search_url)):
            return []

        soup = await self.parse_html_use_soup(html_text)
        pars_data = await self._parse_books(soup)
        logging.info(f"[Yakaboo Parser] Successfully fetched {len(pars_data)}")
        for book in pars_data:
            logging.info(f"[Yakaboo Parser] Fetched {book}")
        return pars_data

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

                url_elem = book.select_one(self.URL_SELECTOR)
                url = (
                    urljoin(self.base_url, url_elem[self.URL_ATTRIBUTE])
                    if url_elem and self.URL_ATTRIBUTE in url_elem.attrs
                    else None
                )
                if not title or not price or not url:
                    logging.warning(
                        f"[Yakaboo Parser] Skipped a card due to missing data: {title}, {price}, {url}"
                    )
                    continue

                books.append({"title": title, "price": price, "url": url})

            except AttributeError:
                logging.warning("[Yakaboo Parser] Skipped a card due to missing data.")
                continue

        return books
