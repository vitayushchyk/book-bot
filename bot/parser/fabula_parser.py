import logging
from typing import List

from bs4 import BeautifulSoup

from bot.parser.base_parser import BaseParser


class FabulaParser(BaseParser):
    BOOK_CONTAINER = ".product__content"
    TITLE_SELECTOR = ".product__title"
    PRICE_SELECTOR_NEW = ".product__price-new"
    PRICE_SELECTOR = ".product__price"
    URL_ATTRIBUTE = "href"
    IN_STOCK_SELECTOR = ".not-available"
    STATUS = "Очікується"

    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

    async def fetch_books_data(self, search_url) -> List[dict]:
        search_url = await self.build_search_url(search_url)
        html_text = await self.fetch_page(search_url)
        if not html_text:
            return []

        soup = await self.parse_html_use_soup(html_text)
        pars_data = await self._parse_books(soup)
        logging.info(f"[Fabula Parser] Fetched {len(pars_data)}")
        for book in pars_data:
            logging.info(f"[Bookling Parser] Book: {book}")
        return pars_data

    async def _parse_books(self, soup: BeautifulSoup) -> List[dict]:
        books = []
        for book in soup.select(self.BOOK_CONTAINER):
            try:

                is_available_elm = book.select_one(self.PRICE_SELECTOR)
                if is_available_elm:
                    is_available_text = is_available_elm.get_text(strip=True)
                    if self.STATUS in is_available_text:
                        logging.warning(
                            "[Fabula Parser] Skipping book as 'NOT AVAILABLE'"
                        )
                        continue

                title_elm = book.select_one(self.TITLE_SELECTOR)
                title = title_elm.get_text(strip=True) if title_elm else None

                price_elm = book.select_one(self.PRICE_SELECTOR_NEW) or book.select_one(
                    self.PRICE_SELECTOR
                )
                raw_price = price_elm.text.strip() if price_elm else "0 грн"
                price = (
                    raw_price.replace(",00 грн", " грн")
                    if raw_price.endswith(",00 грн")
                    else raw_price
                )

                url_elem = title_elm if title_elm else None
                relative_url = url_elem.get(self.URL_ATTRIBUTE) if url_elem else None
                full_url = f"{relative_url}"

                if not title or not price or not full_url:
                    logging.warning(
                        f"[Fabula Parser] Skipped a card due to missing data: {title}, {price}, {full_url}"
                    )
                    continue

                books.append({"title": title, "price": price, "url": full_url})
            except AttributeError as e:
                logging.warning(
                    f"[Fabula Parser]  Skipped a card due to an AttributeError: {e}"
                )
                continue
        return books
