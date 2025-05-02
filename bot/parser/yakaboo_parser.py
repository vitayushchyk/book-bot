import logging
from typing import Any

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin


class YakabooParser(FetchPageMixin):
    def __init__(self, base_url):
        self.base_url = base_url

    BOOK_CONTAINER = "div.category-card"
    TITLE_SELECTOR = "a.ui-card-title.category-card__name"
    PRICE_SELECTOR = "div.category-card__content .category-card__price"
    SPECIAL_PRICE_SELECTOR = ".special-price span"
    URL_SELECTOR = "a.category-card__image"
    URL_ATTRIBUTE = "href"

    async def fetch_books_data(self, query: str) -> list:
        search_url = f"{self.base_url}/search?q={query.strip()}"
        response_text = await self.fetch_page(search_url)

        if not response_text:
            return []

        soup = BeautifulSoup(response_text, features="html.parser")
        book_elements = soup.select(self.BOOK_CONTAINER)

        if not book_elements:
            logging.warning(f"No books found for query: '{query}' in Yakaboo.")
            return []

        books = []
        for book in book_elements:
            try:
                title = await self._get_text_by_selector(book, self.TITLE_SELECTOR)
                price = await self._get_special_or_default_price(book)
                url = await self._get_attribute_by_selector(
                    book, self.URL_SELECTOR, self.URL_ATTRIBUTE, base_url=self.base_url
                )

                if title and url:
                    books.append({"title": title, "price": price, "url": url})
            except Exception as e:
                logging.error(f"Error extracting book data: {e}")

        return books

    async def _get_text_by_selector(self, element, selector: str) -> str | None:
        tag = element.select_one(selector)
        return tag.text.strip() if tag else None

    async def _get_special_or_default_price(self, element) -> str | None:
        prices = element.select(self.PRICE_SELECTOR)

        if not prices:
            return None

        for price in prices:
            special_price = price.select_one(self.SPECIAL_PRICE_SELECTOR)
            if special_price:
                return special_price.text.strip()

        return prices[0].text.strip() if prices else None

    async def _get_attribute_by_selector(
        self, element, selector: str, attribute: str, base_url: str = ""
    ) -> str | None | Any:
        tag = element.select_one(selector)
        if tag and attribute in tag.attrs:
            return f"{base_url}{tag[attribute]}" if base_url else tag[attribute]
        return None
