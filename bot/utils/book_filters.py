from difflib import SequenceMatcher


async def filter_books_by_exact_match(books, search_query):

    filtered_books = [
        book for book in books if search_query.lower() in book["title"].lower()
    ]
    return filtered_books


async def is_similar(title, query):

    similarity = SequenceMatcher(None, title.lower(), query.lower()).ratio()
    return similarity > 0.7


async def filter_books_by_similarity(books, search_query):

    filtered_books = [book for book in books if is_similar(book["title"], search_query)]
    return filtered_books


async def sort_books_by_relevance(books, search_query):

    return sorted(
        books,
        key=lambda book: SequenceMatcher(
            None, book["title"].lower(), search_query.lower()
        ).ratio(),
        reverse=True,
    )
