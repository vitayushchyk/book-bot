import logging
from typing import List

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class FabulaParser(BaseParser, FetchPageMixin):
    BOOK_CONTAINER = ".product__content"
    TITLE_ELEMENT = ".product__title"
    PRICE_ELEMENT_NEW = ".product__price-new"
    PRICE_ELEMENT = ".product__price"
    URL_ATTRIBUTE = "href"

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.base_url}{query.strip()}"
        logging.info(f"[Fabula Parser] Fetching data from URL: {search_url}.")
        html_text = await self.fetch_page(search_url)
        if not html_text:
            logging.warning(
                f"[Fabula Parser] Empty response received for URL: {search_url}."
            )
            return []
        soup = BeautifulSoup(html_text, features="html.parser")
        books = await self._parse_books(soup)
        logging.info(
            f"[Fabula Parser] Successfully fetched {len(books)} books from URL: {search_url}."
        )
        return books

    async def _parse_books(self, soup: BeautifulSoup) -> List[dict]:
        books = []
        for book in soup.select(self.BOOK_CONTAINER):
            try:
                title_elem = book.select_one(self.TITLE_ELEMENT)
                title = title_elem.text.strip()

                price_elem = book.select_one(self.PRICE_ELEMENT_NEW)
                if not price_elem:
                    price_elem = book.select_one(self.PRICE_ELEMENT)
                raw_price = price_elem.text.strip() if price_elem else "0 грн"

                if raw_price.endswith(",00 грн"):
                    price = raw_price.replace(",00 грн", " грн")
                else:
                    price = raw_price

                url_elem = title_elem if title_elem else None
                relative_url = url_elem.get(self.URL_ATTRIBUTE) if url_elem else None
                full_url = f"{relative_url}"

                books.append({"title": title, "price": price, "url": full_url})
                logging.info(
                    f"[Fabula Parser] Parsed book: {title}, Price: {price}, URL: {full_url}"
                )
            except Exception as e:
                logging.warning(f"[Fabula Parser] Skipped a card due to error: {e}")
                continue
        return books
