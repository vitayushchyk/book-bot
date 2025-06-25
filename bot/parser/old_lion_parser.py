import logging
from typing import List

from bs4 import BeautifulSoup

from bot.core.config import settings
from bot.parser.base_parser import BaseParser


class OldLionParser(BaseParser):
    def __init__(self, base_url):
        super().__init__(base_url=base_url, api_url=settings.api_search_url_old_lion)

    PRICE_PARENT_TAG = "div"
    BASE_PRICE_CONTAINER = "ProductCard_price__6Et_j"
    PRICE_CONTAINER = "regular lato-h3 ProductCard_regular__zAIrz"
    IN_STOCK_CONTAINER = "div.product-page__status"
    NOT_AVAILABLE_STATUSES = ["Тираж закінчився", "Тимчасово відсутня"]

    async def fetch_books_data(self, search_url) -> List[dict]:
        search_url = await self.build_search_url(search_url)
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
        for book in books:
            logging.info(f"[[Old Lion Parser] Fetched {book}")
        return books

    async def _parse_books(self, results: list) -> List[dict]:
        books = []
        for book_item in results:
            title = book_item.get("name")
            book_type = book_item.get("type")
            slug = book_item.get("slug")

            if not slug:
                continue

            url = f"{self.base_url}{slug}"

            price = 0
            if book_type in ("book", "ebook"):
                html = await self.fetch_page(url)
                if html:
                    try:
                        soup = BeautifulSoup(html, features="html.parser")

                        is_available_elm = soup.select_one(self.IN_STOCK_CONTAINER)
                        if is_available_elm:

                            is_available = is_available_elm.get_text(strip=True)

                            if any(
                                status in is_available
                                for status in self.NOT_AVAILABLE_STATUSES
                            ):
                                logging.warning(
                                    f"[Old Lion Parser] Skipping book '{title}' as 'NOT AVAILABLE'"
                                )
                                continue

                        # get price
                        price_containers = soup.find_all(
                            self.PRICE_PARENT_TAG,
                            class_=lambda x: x and self.BASE_PRICE_CONTAINER in x,
                        )

                        for container in price_containers:
                            price_elm = container.find(
                                self.PRICE_PARENT_TAG, class_=self.PRICE_CONTAINER
                            )

                            if price_elm:
                                try:

                                    price_text = (
                                        price_elm.text.strip()
                                        .replace("грн", "")
                                        .strip()
                                    )

                                    price_text = price_text.split(".")[0]

                                    price = price_text

                                    break
                                except Exception as e:
                                    logging.error(
                                        f"[Old Lion Parser] Error parsing price for {url}: {e}"
                                    )
                                    continue

                    except Exception as e:
                        logging.error(
                            f"[Old Lion Parser] Error parsing price for {url}: {e}"
                        )
                        continue

            books.append(
                {
                    "title": title,
                    "url": url,
                    "price": price,
                }
            )
        return books
