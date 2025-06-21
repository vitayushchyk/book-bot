import logging
from typing import List

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.core.config import settings
from bot.parser.base_parser import BaseParser


class OldLionParser(BaseParser, FetchPageMixin):
    def __init__(self, base_url):
        super().__init__(base_url=base_url)
        self.api_url = settings.api_search_url_old_lion

    PRICE_PARENT_TAG = "div"
    PRICE_PARENT_CLASS = "product-price ProductCard_price__6Et_j ProductCard_books-wrapper__7G0_l ProductCard_single__BP5h_"
    PRICE_CHILD_CLASS = "regular lato-h3 ProductCard_regular__zAIrz"

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.api_url}{query.strip()}"
        logging.info(f"[Old Lion Parser] Fetching data from URL: {search_url}.")
        response_text = await self.fetch_page(search_url)

        if not response_text:
            return []

        try:
            data = await self._parse_json(response_text)
            results = data.get("data", [])
        except Exception as e:
            logging.error(f"[Old Lion Parser] Error parsing data: {e}")
            return []

        books = await self._parse_books(results)
        logging.info(f"[Old Lion Parser] Successfully fetched {len(books)} books.")
        return books

    async def _parse_books(self, results: list) -> List[dict]:
        books = []
        for book_item in results:
            title = book_item.get("name", "Title not available")
            slug = book_item.get("slug")
            if not slug:
                logging.warning(
                    f"[Old Lion Parser] Skipping book without slug: {book_item}"
                )
                continue
            url = f"{self.base_url}{slug}"
            price = await self._get_book_price(url)
            books.append({"title": title, "url": url, "price": price})
        return books

    async def _get_book_price(self, url: str) -> str:
        html = await self.fetch_page(url)
        if not html:
            return "Price not available"

        try:
            soup = BeautifulSoup(html, features="html.parser")
            return self._parse_price(soup)
        except Exception as e:
            logging.error(f"[Old Lion Parser] Error parsing price for {url}: {e}")
            return "Price not available"

    def _parse_price(self, soup: BeautifulSoup) -> str:
        price_div = soup.find(self.PRICE_PARENT_TAG, class_=self.PRICE_PARENT_CLASS)
        if price_div:
            price = price_div.find("div", class_=self.PRICE_CHILD_CLASS)
            if price:
                price_text = price.text.strip().replace(",", "").replace(" ", "")
                try:
                    numeric_price = "".join(
                        c for c in price_text if c.isdigit() or c == "."
                    )
                    price_value = int(float(numeric_price))
                    return str(price_value)
                except ValueError:
                    return "Price not available"
        return "Price not available"
