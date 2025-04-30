import logging
from typing import Any

import requests
from bs4 import BeautifulSoup


class YakabooParser:
    def __init__(self, base_url):
        self.base_url = base_url

    BOOK_CONTAINER = "div.category-card"
    TITLE_SELECTOR = "a.ui-card-title.category-card__name"
    PRICE_SELECTOR = "div.category-card__content .category-card__price"
    URL_SELECTOR = "a.category-card__image"
    URL_ATTRIBUTE = "href"

    async def fetch_books_data(self, query: str) -> list:
        search_url = f"{self.base_url}/search?q={query.strip()}"

        try:
            response = requests.get(search_url)
            response.raise_for_status()

            if response.encoding.lower() != "utf-8":
                response.encoding = "utf-8"

            soup = BeautifulSoup(response.text, features="html.parser")
            book_elements = soup.select(self.BOOK_CONTAINER)

            if not book_elements:
                logging.warning(f"No books found for query: '{query}'.")
                return []

            books = []
            for book in book_elements:
                try:

                    title = self._extract_text(book, self.TITLE_SELECTOR)
                    price = self._extract_text(book, self.PRICE_SELECTOR)
                    url = self._extract_attribute(
                        book,
                        self.URL_SELECTOR,
                        self.URL_ATTRIBUTE,
                        base_url=self.base_url,
                    )

                    if title and url:
                        books.append({"title": title, "price": price, "url": url})
                except Exception as e:
                    logging.error(f"Error extracting book data: {e}")

            return books
        except requests.exceptions.RequestException as ex:
            logging.error(f"HTTP error while fetching data: {ex}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error in fetch_books_data: {e}")
            return []

    def _extract_text(self, element, selector: str) -> str:
        tag = element.select_one(selector)
        return tag.text.strip() if tag else None

    def _extract_attribute(
        self, element, selector: str, attribute: str, base_url: str = ""
    ) -> str | None | Any:
        tag = element.select_one(selector)
        if tag and attribute in tag.attrs:
            return f"{base_url}{tag[attribute]}" if base_url else tag[attribute]
        return None
