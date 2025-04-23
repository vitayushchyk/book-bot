import logging

import requests
from bs4 import BeautifulSoup

from bot.base.base_shop import BaseShop
from bot.core.config import settings
from bot.utils.book_details import get_book_details
from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_price,
    sort_books_by_relevance,
)


class Readeat(BaseShop):
    async def get_book(self, book_name):
        search_url_readeat = f"{settings.search_url_readeat}{book_name}"

        try:
            response = requests.get(search_url_readeat)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, features="html.parser")

            books = []
            filter_titles = set()
            book_elements = soup.select("div.fn_product.card.product-card")

            for index, book_element in enumerate(book_elements, start=1):
                try:
                    book_data = {
                        "title": book_element.get(
                            key="data-name", default="Title not available"
                        ),
                        "price": f"{book_element.get(key='data-price', default='Price not available')} грн",
                        "url": (
                            book_element.select_one("a.d-block")["href"]
                            if book_element.select_one("a.d-block")
                            else "URL not available"
                        ),
                    }

                    book_details = await get_book_details(
                        book_data, source_type="readeat"
                    )

                    if book_details and book_details["title"] not in filter_titles:
                        books.append(book_details)
                        filter_titles.add(book_details["title"])
                    else:
                        logging.warning(
                            f"Skipping duplicate or incomplete book {index}: {book_data.get('title')}"
                        )

                except Exception as e:
                    logging.error(f"Error processing book {index}: {e}")

            books = await filter_books_by_exact_match(books, book_name)

            if not books:
                books = await filter_books_by_similarity(books, book_name)

            books = await sort_books_by_relevance(books, book_name)
            books = await sort_books_by_price(books)

            return books

        except requests.RequestException as e:
            logging.error(f"Error during HTTP request: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return []
