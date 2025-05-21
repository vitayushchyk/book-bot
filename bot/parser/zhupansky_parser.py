import json
import logging
from typing import List, Optional

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.parser.base_parser import BaseParser


class ZhupanskyParser(BaseParser, FetchPageMixin):
    PRICE_ELEMENT = "p.price span.woocommerce-Price-amount bdi"
    PRICE_META = "meta[itemprop=price]"
    SELECTOR_BOOK = "ul.et-result-products > li"
    TITLE_SELECTOR = "a"

    def __init__(
        self,
        base_url: str,
    ):
        super().__init__(base_url=base_url)
        self.search_params = {
            "products": 1,
            "action": "et_get_search_result",
        }

    async def fetch_books_data(self, query: str) -> List[dict]:
        params = self.search_params.copy()
        params["s"] = query

        try:

            base_url = self.base_url
            query_string = "&".join(f"{key}={value}" for key, value in params.items())
            search_url = f"{base_url}?{query_string}"

            response_text = await self.fetch_page(search_url)
            if not response_text:
                logging.warning("[Zhupansky Parser] No response received from server.")
                return []

            json_data = json.loads(response_text)
            embedded_html = json_data.get("html", "")
            if not embedded_html:
                logging.warning(
                    "[Zhupansky Parser] Field 'html' not found in JSON response."
                )
                return []

            soup = BeautifulSoup(embedded_html, features="html.parser")
            books = soup.select(self.SELECTOR_BOOK)

            logging.info(
                f"[Zhupansky Parser] Found {len(books)} books in search results."
            )

            detailed_books = []
            for book in books:
                title_el = book.select_one(self.TITLE_SELECTOR)
                title = title_el.text.strip() if title_el else "Title not available"
                link = (
                    title_el["href"]
                    if title_el and "href" in title_el.attrs
                    else "Link not available"
                )

                price = (
                    await self._fetch_book_price(link)
                    if link != "Link not available"
                    else "Price not available"
                )

                detailed_books.append({"title": title, "link": link, "price": price})

            return detailed_books

        except Exception as e:
            logging.error(
                f"[Zhupansky Parser] Error while fetching books: {e}", exc_info=True
            )
            return []

    async def _fetch_book_price(self, book_link: str) -> Optional[str]:
        try:
            response_text = await self.fetch_page(book_link)
            if not response_text:
                logging.warning(
                    f"[Zhupansky Parser] No response for book link: {book_link}"
                )
                return "Price not available"
            product_soup = BeautifulSoup(response_text, features="html.parser")
            price_meta = product_soup.select_one(self.PRICE_META)
            if price_meta and price_meta.get("content"):
                return f"{price_meta['content']} грн"

            price_element = product_soup.select_one(self.PRICE_ELEMENT)
            if price_element:
                return price_element.text.strip()
            return "Price not available"
        except Exception as e:
            logging.error(
                f"[Zhupansky Parser] Error fetching price for book: {e}", exc_info=True
            )
            return "Price not available"
