# import logging
# from typing import Dict, List
#
# import aiohttp
#
#
# from bot.utils.book_filters import (
#     filter_books_by_exact_match,
#     filter_books_by_similarity,
#     sort_books_by_price,
#     sort_books_by_relevance,
# )
#
#
# class FetchBooksMixin:
#     async def fetch_books(
#         self, search_url: str, source_type: str, book_name: str
#     ) -> List[Dict]:
#         if not search_url or not search_url.startswith("http"):
#             logging.error(f"Invalid search URL: {search_url} for {source_type}")
#             return []
#
#         if not source_type or not book_name:
#             logging.error("Source type or book name is missing.")
#             return []
#
#         try:
#             logging.info(f"Fetching URL: {search_url}")
#
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(search_url, timeout=5) as response:
#                     if response.status != 200:
#                         logging.error(
#                             f"Failed to fetch data. HTTP status code: {response.status}"
#                         )
#                         return []
#
#                     data = await response.json()
#
#             logging.info("Data successfully fetched.")
#             books = []
#             filter_titles = set()
#
#             item_groups = data.get("results", {}).get("item_groups", [])
#             for group in item_groups:
#                 for item in group.get("items", []):
#                     try:
#                         formatted_book = await get_book_details(
#                             item, source_type=source_type
#                         )
#                         if (
#                             formatted_book
#                             and formatted_book["title"] not in filter_titles
#                         ):
#                             books.append(formatted_book)
#                             filter_titles.add(formatted_book["title"])
#                             logging.info(f"Added book: {formatted_book['title']}")
#                         else:
#                             logging.warning(
#                                 f"Skipping duplicate or incomplete book: {item.get('name', 'No title provided')}"
#                             )
#                     except KeyError as e:
#                         logging.error(f"Missing key in item data: {e}")
#                     except Exception as e:
#                         logging.error(f"Error processing book: {e}")
#                         continue
#
#             if books:
#                 books = await filter_books_by_exact_match(books, book_name)
#                 if not books:
#                     books = await filter_books_by_similarity(books, book_name)
#                 if books:
#                     books = await sort_books_by_relevance(books, book_name)
#                     books = await sort_books_by_price(books)
#
#             return books
#
#         except aiohttp.ClientError as e:
#             logging.error(f"API request error: {e}")
#             return []
#         except Exception as e:
#             logging.error(f"Unexpected error while fetching books: {e}")
#             return []
