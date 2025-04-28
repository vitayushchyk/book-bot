import asyncio
import logging

from bot.utils.book_details import get_book_details
from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_price,
    sort_books_by_relevance,
)


class BaseProcessor:
    def __init__(self, source_type: str):
        self.source_type = source_type

    async def add_details_to_books(self, books: list) -> list:
        unique_titles = set()

        async def process_book(book):
            try:

                book_details = await get_book_details(
                    book, source_type=self.source_type
                )

                if book_details and book_details["title"] not in unique_titles:
                    unique_titles.add(book_details["title"])
                    return book_details
                else:
                    logging.warning(
                        f"Skipping duplicate or incomplete book: {book} from {self.source_type.lower()}"
                    )
            except Exception as e:
                logging.error(
                    f"Error processing book details: {e} from {self.source_type.upper()}"
                )
            return None

        # TODO: Подумати про використання asyncio.gather для великих списків.
        # Аргумент: Велика кількість мережевих викликів може викликати навантаження.
        # Пропозиція: Додати обмеження за допомогою asyncio.Semaphore.

        processed_books = await asyncio.gather(*(process_book(book) for book in books))

        return [book for book in processed_books if book]

    async def filter_and_sort_books(self, books: list, query: str) -> list:
        logging.info(
            f"Books before filtering: {len(books)} from {self.source_type.upper()}"
        )

        books_by_exact_match = await filter_books_by_exact_match(books, query)

        if books_by_exact_match:
            books_to_sort = books_by_exact_match
        else:
            books_to_sort = await filter_books_by_similarity(books, query)

        logging.info(
            f"Books after filtering: {len(books_to_sort)} from {self.source_type.upper()}"
        )

        sorted_books_by_relevance = await sort_books_by_relevance(books_to_sort, query)
        sorted_books_by_price = await sort_books_by_price(sorted_books_by_relevance)

        logging.info(
            f"Books after sorting: {len(sorted_books_by_price)} from {self.source_type.upper()}"
        )
        return sorted_books_by_price
