import logging
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from bot.parser.base_parser import BaseParser


class SensBookParser(BaseParser):
    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

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
        search_url = await self.build_search_url(query=query)

        if not (html_text := await self.fetch_page(search_url)):
            return []
        soup = await self.parse_html_use_soup(html_text)
        pars_data = await self._parse_books(soup)
        logging.info(f"[Sens Parser] Successfully fetched {len(pars_data)}")
        for book in pars_data:
            logging.info(f"Fetched {book}")
        return pars_data

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
                if not title or not price or not link:
                    logging.warning(
                        f"[Sens Parser] Skipped a card due to missing data: {title}, {price}, {link}"
                    )
                    continue
                if not title or not price or not link:
                    logging.warning(
                        f"[Sens Parser] Skipped a card due to missing data: {title}, {price}, {link}"
                    )
                books.append({"title": title, "price": price, "url": link})

            except AttributeError as e:
                logging.warning(
                    f"[Sens Parser] SSkipped a card due to an AttributeError: {e}"
                )
                continue

        return books
