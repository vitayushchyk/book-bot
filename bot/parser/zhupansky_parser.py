import logging
from typing import List

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
            logging.info(f"[Zhupansky Parser] Fetching data from URL: {search_url}")

            response_text = await self.fetch_page(search_url)
            if not response_text:
                return []
            data = await self._parse_json(response_text)
            embedded_html = data.get("html", "")
            if not embedded_html:
                return []

            books = await self._parse_books(embedded_html)
            logging.info(
                f"[Zhupansky Parser] Successfully parsed {len(books)} books from URL: {search_url}"
            )
            return books

        except Exception as e:
            logging.error(
                f"[Zhupansky Parser] Error while fetching books: {e}", exc_info=True
            )
            return []

    async def _parse_books(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, features="html.parser")
        book_elements = soup.select(self.SELECTOR_BOOK)
        books = []
        for book in book_elements:
            title_elm = book.select_one(self.TITLE_SELECTOR)
            title = title_elm.text.strip() if title_elm else None
            link = (
                title_elm["href"]
                if title_elm and "href" in title_elm.attrs
                else "Link not available"
            )

            if link != "Link not available":
                try:
                    response_text = await self.fetch_page(link)
                    if response_text:
                        product_soup = BeautifulSoup(
                            response_text, features="html.parser"
                        )
                        price_meta = product_soup.select_one(self.PRICE_META)
                        if price_meta and price_meta.get("content"):
                            price = f"{price_meta['content']}"
                        else:
                            price_elm = product_soup.select_one(self.PRICE_ELEMENT)
                            if price_elm:
                                price = price_elm.text.strip()
                            else:
                                price = 0
                    else:
                        price = 0
                except Exception as e:
                    logging.error(
                        f"[Zhupansky Parser] Error fetching price for book: {e}",
                        exc_info=True,
                    )
                    price = 0
            else:
                price = 0

            books.append({"title": title, "link": link, "price": price})
        return books
