import logging

from bot.utils.book_details import get_book_details
from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_price,
    sort_books_by_relevance,
)


class BookFilterAndSorter:
    @staticmethod
    async def filter_and_sort_books(books: list, query: str) -> list:
        logging.info(f"Books before filtering: {len(books)}")
        filtered_books = await filter_books_by_exact_match(books, query)

        if not filtered_books:
            filtered_books = await filter_books_by_similarity(books, query)

        logging.info(f"Books after filtering: {len(filtered_books)}")

        sorted_books_by_relevance = await sort_books_by_relevance(filtered_books, query)
        sorted_books_by_price = await sort_books_by_price(sorted_books_by_relevance)

        logging.info(f"Books after sorting by price: {len(sorted_books_by_price)}")
        return sorted_books_by_price


class BookDetailsAdder:
    @staticmethod
    async def add_details_to_books(books: list) -> list:
        processed_books = []
        seen_titles = set()

        for book in books:
            try:
                book_details = await get_book_details(book, source_type="bookling")
                if book_details and book_details["title"] not in seen_titles:
                    processed_books.append(book_details)
                    seen_titles.add(book_details["title"])
                else:
                    logging.warning(f"Skipping duplicate or incomplete book: {book}")
            except Exception as e:
                logging.error(f"Error processing book details: {e}")

        return processed_books
