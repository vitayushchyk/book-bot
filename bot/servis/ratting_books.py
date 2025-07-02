import json
import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Union

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin
from bot.core.config import settings

NO_RATING = "Воу, з відгуками в прольоті"
NO_TITLE = "Ноу-ноу-ноу, з тайтлом біда"
NO_DESCRIPTION = "Щось з дескріпшином натупив, пішов фіксить"
NO_AUTHORS = "Десь загубився"
EXCLUDED_LANGUAGE = "ru"


class RattingBooks(FetchPageMixin):
    def __init__(self, api_key: str, excluded_language: str = EXCLUDED_LANGUAGE):
        self.api_key = api_key
        self.google_rating_url = settings.google_rating
        self.excluded_language = excluded_language

    async def _fetch_books_from_api(self, query: str) -> Optional[Dict[str, Any]]:

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
            return None
        except Exception as e:
            logging.exception(f"Unknown exception while parsing books response: {e}")
            return None

    async def _filter_books(self, books: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        filtered = [
            book
            for book in books
            if book.get("volumeInfo", {}).get("language", "") != self.excluded_language
        ]
        logging.info(
            f"Filtered out {len(books) - len(filtered)} '{self.excluded_language}' books"
        )
        return filtered

    async def _extract_book_with_rating(
        self, books: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        for book in books:
            info = book.get("volumeInfo", {})
            if "averageRating" in info:
                logging.info(
                    f"Found book with API rating: {info.get('title', '<no title>')} - {info['averageRating']}"
                )
                return await self._format_book_info(book, info["averageRating"])
        return None

    async def _parse_rating_from_html(self, html: str) -> Optional[float]:

        try:
            soup = BeautifulSoup(html, "html.parser")
            rating_divs = soup.find_all("div", class_="TT9eCd")
            for div in rating_divs:
                aria_label = div.get("aria-label", "")
                if aria_label and "Оцінка:" in aria_label:
                    match = re.search(r"Оцінка:\s*([\d,\.]+)", aria_label)
                    if match:
                        rating_val = match.group(1).replace(",", ".")
                        try:
                            return float(rating_val)
                        except ValueError as ve:
                            logging.warning(
                                f"Failed to convert aria rating '{rating_val}': {ve}"
                            )
                text = div.text.strip().replace(",", ".")
                match = re.match(r"^([\d\.]+)", text)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError as ve:
                        logging.warning(
                            f"Failed to convert text rating '{match.group(1)}': {ve}"
                        )
        except Exception as e:
            logging.exception(f"Exception when parsing HTML for rating: {e}")
        return None

    async def _parse_rating_from_link(self, buy_link: str) -> Union[float, str]:

        try:
            page_response = await self.fetch_page(buy_link)
            if page_response:
                rating = await self._parse_rating_from_html(page_response)
                if rating is not None:
                    logging.info(f"Parsed buy link rating: {rating} ({buy_link})")
                    return rating
                else:
                    logging.info(f"No rating found via buy link: {buy_link}")
            return NO_RATING
        except Exception as e:
            logging.error(f"Error while fetching/parsing buy link '{buy_link}': {e}")
            return NO_RATING

    async def _extract_book_with_buy_link(
        self, books: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        for book in books:
            sale_info = book.get("saleInfo", {})
            buy_link = sale_info.get("buyLink")
            if buy_link:
                rating = await self._parse_rating_from_link(buy_link)
                return await self._format_book_info(book, rating)
        return None

    async def _format_book_info(
        self, book: Dict[str, Any], rating: Union[float, str]
    ) -> Dict[str, Any]:

        info = book.get("volumeInfo", {})
        title = info.get("title", NO_TITLE)
        description = info.get("description", NO_DESCRIPTION)
        authors = ", ".join(info.get("authors", [NO_AUTHORS]))
        return {
            "title": title,
            "description": description,
            "authors": authors,
            "rating": rating,
        }

    async def search_book(self, query: str) -> Optional[Dict[str, Any]]:
        data = await self._fetch_books_from_api(query)
        if not data or "items" not in data or not data["items"]:
            logging.info(f"No books found for query: {query}")
            return None

        valid_books = await self._filter_books(data["items"])

        book_with_rating = await self._extract_book_with_rating(valid_books)
        if book_with_rating:
            return book_with_rating

        book_with_buy_link = await self._extract_book_with_buy_link(valid_books)
        if book_with_buy_link:
            return book_with_buy_link

        logging.info(f"No books with ratings or buy links found for query: {query}")
        return None
