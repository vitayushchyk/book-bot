import logging
from abc import ABC, abstractmethod
from typing import Any

from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_price,
    sort_books_by_relevance,
)


class BaseProcessor(ABC):

    @property
    def title_key(self):
        return "title"

    @property
    def price_key(self):
        return "price"

    @property
    def link_key(self):
        return "url"

    @property
    @abstractmethod
    def shop_name(self): ...

    def prepare_book_details(self, book: dict) -> dict[str, str | Any] | None:
        try:
            title = book.get(self.title_key, "Title not available")
            price = book.get(self.price_key, "Price not available")
            link = book.get(self.link_key, "#")

            if isinstance(price, str):
                price = price.replace(" ", "")
                if price.isdigit():
                    price = f"{price} грн"
            elif isinstance(price, (int, float)):
                price = f"{int(price)} грн"

            return {
                "title": title,
                "price": price,
                "link": link,
                "shop": self.shop_name,
            }
        except Exception as e:
            logging.error(
                f"Error in prepare_book_details: {e} in {self.shop_name.upper()}"
            )
            return None

    async def add_details_to_books(self, books: list) -> list:
        unique_titles = set()

        async def process_book(book):
            try:
                book_details = self.prepare_book_details(book)

                if book_details and book_details["title"] not in unique_titles:
                    unique_titles.add(book_details["title"])
                    return book_details
                else:
                    logging.warning(
                        f"Skipping duplicate or incomplete book: {book} from {self.shop_name.upper()}"
                    )
            except Exception as e:
                logging.error(
                    f"Error processing book details: {e} from {self.shop_name.upper()}"
                )
            return None

        processed_books = []
        for book in books:
            processed_book = await process_book(book)
            if processed_book:
                processed_books.append(processed_book)

        return processed_books

    async def filter_and_sort_books(self, books: list, query: str) -> list:
        logging.info(
            f"Books before filtering: {len(books)} from {self.shop_name.upper()}"
        )

        books_by_exact_match = await filter_books_by_exact_match(books, query)

        if books_by_exact_match:
            books_to_sort = books_by_exact_match
        else:
            books_to_sort = await filter_books_by_similarity(books, query)

        logging.info(
            f"Books after filtering: {len(books_to_sort)} from {self.shop_name.upper()}"
        )

        sorted_books_by_relevance = await sort_books_by_relevance(books_to_sort, query)
        sorted_books_by_price = await sort_books_by_price(sorted_books_by_relevance)

        logging.info(
            f"Books after sorting: {len(sorted_books_by_price)} from {self.shop_name.upper()}"
        )
        return sorted_books_by_price
