import logging
import re
from difflib import SequenceMatcher


async def _normalize_title_text(text):
    return re.sub(r"[^\w\s]", "", text).lower()


async def filter_books_by_exact_match(books, search_query):
    normalized_query = await _normalize_title_text(search_query)
    filtered_books = [
        book
        for book in books
        if normalized_query in await _normalize_title_text(book["title"])
    ]
    logging.info(f"Filtered books by exact match: {filtered_books}")
    return filtered_books


async def is_similar(title, query):
    normalized_title = await _normalize_title_text(title)
    normalized_query = await _normalize_title_text(query)
    similarity = SequenceMatcher(None, normalized_title, normalized_query).ratio()
    logging.info(f"Similarity between '{title}' and '{query}': {similarity}")
    return similarity > 0.7


async def filter_books_by_similarity(books, search_query):
    filtered_books = [
        book for book in books if await is_similar(book["title"], search_query)
    ]
    logging.info(f"Filtered books by similarity: {filtered_books}")
    return filtered_books


async def sort_books_by_relevance(books, search_query):
    normalized_query = await _normalize_title_text(search_query)

    books_with_normalized_titles = [
        {**book, "normalized_title": await _normalize_title_text(book["title"])}
        for book in books
    ]
    result = sorted(
        books_with_normalized_titles,
        key=lambda book: SequenceMatcher(
            None,
            book["normalized_title"],
            normalized_query,
        ).ratio(),
        reverse=True,
    )
    logging.info(f"Sorted books by relevance: {result}")
    return result


async def _normalize_price(price):
    clean_price = price.replace(" ", "").replace(",", ".")
    clean_price = "".join(char for char in clean_price if char.isdigit() or char == ".")
    return float(clean_price)


async def sort_books_by_price(books):
    books_with_prices = [
        {**book, "normalized_price": await _normalize_price(book["price"])}
        for book in books
    ]
    logging.info(f"Books with normalized prices: {books_with_prices}")
    return sorted(books_with_prices, key=lambda book: book["normalized_price"])
