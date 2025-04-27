import logging

from bot.utils.book_details import get_book_details
from bot.utils.book_filters import (
    filter_books_by_exact_match,
    filter_books_by_similarity,
    sort_books_by_price,
    sort_books_by_relevance,
)


class YakabooBookProcessor:
    @staticmethod
    async def filter_and_sort_books(books: list, query: str) -> list:
        filtered_books = await filter_books_by_exact_match(books, query)
        logging.info(f"Books before filtering: {len(books)}")

        if not filtered_books:
            filtered_books = await filter_books_by_similarity(books, query)
        logging.info(f"Books after filtering: {len(filtered_books)}")

        sorted_books = await sort_books_by_relevance(filtered_books, query)
        sorted_books = await sort_books_by_price(sorted_books)

        return sorted_books

    @staticmethod
    async def add_details_to_books(books: list) -> list:
        processed_books = []
        seen_titles = set()

        for book in books:
            try:
                book_details = await get_book_details(book, source_type="yakaboo")
                if book_details and book_details["title"] not in seen_titles:
                    processed_books.append(book_details)
                    seen_titles.add(book_details["title"])
                else:
                    logging.warning(f"Skipping duplicate or incomplete book: {book}")
            except Exception as e:
                logging.error(f"Error processing Yakaboo book details: {e}")

        return processed_books
