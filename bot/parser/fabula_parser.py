import logging
from typing import List

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class FabulaParser(BaseParser, FetchPageMixin):
    BOOK_CONTAINER = ".product__content"
    TITLE_SELECTOR = ".product__title"
    PRICE_SELECTOR_NEW = ".product__price-new"
    PRICE_SELECTOR = ".product__price"
    URL_ATTRIBUTE = "href"
    IN_STOCK_SELECTOR = ".not-available"

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

                availability_element = book.select_one(self.PRICE_SELECTOR)
                if availability_element:
                    availability_text = availability_element.get_text(strip=True)
                    if "Очікується" in availability_text:
                        logging.debug("[Fabula Parser] Skipping book as 'OUT OF STOCK'")
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

                books.append({"title": title, "price": price, "url": full_url})
                logging.info(
                    f"[Fabula Parser] Parsed book: {title}, Price: {price}, URL: {full_url}"
                )
            except AttributeError as e:
                logging.warning(f"[Fabula Parser] Skipped a card due to error: {e}")
                continue
        return books
