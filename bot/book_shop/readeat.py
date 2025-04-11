import logging

import requests
from bs4 import BeautifulSoup

from bot.book_shop.base_shop import BaseShop
from bot.core.config import settings
from bot.utils.book_details import get_book_details


class Readeat(BaseShop):
    async def get_book(self, book_name):
        search_url_readeat = f"{settings.search_url_readeat}{book_name}"

        try:
            response = requests.get(search_url_readeat)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, features="html.parser")

            books = []
            book_elements = soup.select("div.fn_product.card.product-card")

            for index, book_element in enumerate(book_elements, start=1):
                try:

                    book_data = {
                        "title": book_element.get("data-name", "Title not available"),
                        "price": f"{book_element.get('data-price', 'Price not available')} грн",
                        "url": (
                            book_element.select_one("a.d-block")["href"]
                            if book_element.select_one("a.d-block")
                            else "URL not available"
                        ),
                    }

                    book_details = await get_book_details(
                        book_data, source_type="readeat"
                    )

                    if book_details:
                        books.append(book_details)

                    else:
                        logging.warning(
                            f"Skipping book {index} due to missing details."
                        )

                except Exception as e:
                    logging.error(f"Error processing book {index}: {e}")

            return books

        except requests.RequestException as e:
            logging.error(f"Error during HTTP request: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return []
