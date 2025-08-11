import json
import logging
import urllib.parse
from typing import Any, Dict, List, Optional, Union

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.core.config import settings
from bot.servis.ratting_base import EXCLUDED_LANGUAGE, NO_RATING, RattingBooksBase


class RattingBooks(RattingBooksBase, FetchPageMixin):
    def __init__(self, api_key: str, excluded_language: str = EXCLUDED_LANGUAGE):
        super().__init__(excluded_language)
        self.api_key = api_key
        self.google_rating_url = settings.google_rating

    async def fetch_books_from_api(self, query: str) -> Optional[Dict[str, Any]]:

        params = {"q": query, "key": self.api_key}
        encoded_params = urllib.parse.urlencode(params)
        full_url = f"{self.google_rating_url}?{encoded_params}"
        logging.info(f"Requesting books with URL: {full_url}")
        result = await self.fetch_page(full_url)
        if not result:
            logging.warning(f"No response for query '{query}' from API")
            return None
        try:
            data = json.loads(result)
            logging.debug(f"Received data for '{query}': {data}")
            return data
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error for books API response: {e}")
        except Exception as e:
            logging.exception(f"Unknown exception while parsing books response: {e}")
        return None

    async def extract_book_with_rating(
        self, books: List[Dict[str, Any]], limit: int = 5
    ) -> List[Dict[str, Any]]:
        results = []
        for book in books:
            info = book.get("volumeInfo", {})
            rating = info.get("averageRating", None)
            if isinstance(rating, (int, float)):
                logging.info(
                    f"Found book with API rating: {info.get('title', '<no title>')} - {rating}"
                )
                formatted = self.format_for_tg(book, rating)
                results.append(formatted)
                if len(results) >= limit:
                    break
        return results

    async def parse_rating_from_link(self, buy_link: str) -> Union[float, str]:
        try:
            page_response = await self.fetch_page(buy_link)
            if page_response:
                rating = self.parse_rating_from_html(page_response)
                if rating is not None:
                    logging.info(f"Parsed buy link rating: {rating} ({buy_link})")
                    return rating
                else:
                    logging.info(f"No rating found via buy link: {buy_link}")
            return NO_RATING
        except Exception as e:
            logging.error(f"Error while fetching/parsing buy link '{buy_link}': {e}")
            return NO_RATING

    async def extract_book_with_buy_link(
        self, books: List[Dict[str, Any]], limit: int = 5
    ) -> List[Dict[str, Any]]:
        import asyncio

        results = []
        tasks = []
        books_with_links = []
        for book in books:
            sale_info = book.get("saleInfo", {})
            buy_link = sale_info.get("buyLink")
            if buy_link:
                tasks.append(self.parse_rating_from_link(buy_link))
                books_with_links.append(book)
                if len(tasks) >= limit:
                    break

        ratings = await asyncio.gather(*tasks)
        for book, rating in zip(books_with_links, ratings):
            formatted = self.format_for_tg(book, rating)
            results.append(formatted)
        return results

    async def search_book(
        self, query: str, limit: int = 5
    ) -> Optional[List[Dict[str, Any]]]:
        data = await self.fetch_books_from_api(query)
        if not data or "items" not in data or not data["items"]:
            logging.info(f"No books found for query: {query}")
            return None

        valid_books = self.filter_books(data["items"])

        books_with_ratings = await self.extract_book_with_rating(valid_books, limit)
        if books_with_ratings:
            return books_with_ratings

        books_with_buy_links = await self.extract_book_with_buy_link(valid_books, limit)
        if books_with_buy_links:
            return books_with_buy_links

        logging.info(f"No books with ratings or buy links found for query: {query}")
        return None
