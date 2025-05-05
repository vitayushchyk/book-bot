import logging
from typing import List

import requests
from bs4 import BeautifulSoup


class ZhupanskyParser:
    def __init__(self, baseurl: str, headers: dict):

        self.baseurl = baseurl
        self.headers = headers

    PRICE_ELEMENT = "p.price span.woocommerce-Price-amount bdi"
    PRICE_META = "meta[itemprop=price]"
    SELECTOR_BOOK = "ul.et-result-products > li"
    TITLE_SELECTOR = "a"

    def fetch_books_html(self, query: str) -> List[dict]:
        params = {
            "s": query,
            "products": 1,
            "count": 3,
            "images": 1,
            "posts": 1,
            "portfolio": 1,
            "pages": 1,
            "action": "et_get_search_result",
        }
        try:
            response = requests.get(self.baseurl, headers=self.headers, params=params)
            response.raise_for_status()
            json_data = response.json()

            if not json_data or "html" not in json_data:
                logging.warning(
                    "[Zhupansky Parser] Field 'html' not found in the JSON response."
                )
                return []

            embedded_html = json_data["html"]
            soup = BeautifulSoup(embedded_html, features="html.parser")
            books = soup.select(self.SELECTOR_BOOK)
            logging.info(
                f"[Zhupansky Parser] Found {len(books)} books in the search results."
            )

            raw_books = []
            for book in books:
                title_el = book.select_one(self.TITLE_SELECTOR)
                title = title_el.text.strip() if title_el else "Title not available"
                link = (
                    title_el["href"]
                    if title_el and "href" in title_el.attrs
                    else "Link not available"
                )

                raw_books.append({"title": title, "link": link})
            return raw_books

        except requests.exceptions.RequestException as e:
            logging.error(f"[Zhupansky Parser] Request error while fetching books: {e}")
            return []

    def fetch_book_price(self, book_link: str) -> str:
        try:
            response = requests.get(book_link, headers=self.headers)
            response.raise_for_status()

            product_soup = BeautifulSoup(response.text, features="html.parser")
            price_meta = product_soup.select_one(self.PRICE_META)
            if price_meta and price_meta.get("content"):
                return f'{price_meta["content"]} грн'

            price_element = product_soup.select_one(self.PRICE_ELEMENT)
            if price_element:
                return price_element.text.strip()

            return "Price not available"
        except requests.exceptions.RequestException as e:
            logging.error(
                f" [Zhupansky Parser] Error fetching product price for {book_link}: {e}"
            )
            return "Price not available"
