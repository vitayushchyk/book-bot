import logging
import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Union

from bs4 import BeautifulSoup

NO_RATING = "Воу, з відгуками в прольоті"
NO_TITLE = "Ноу-ноу-ноу, з тайтлом біда"
NO_DESCRIPTION = "Щось з дескріпшином натупив, пішов фіксить"
NO_AUTHORS = "Десь загубився"
EXCLUDED_LANGUAGE = "ru"


class RattingBooksBase:
    def __init__(self, excluded_language: str = EXCLUDED_LANGUAGE):
        self.excluded_language = excluded_language

    def extract_volume_info(self, book: Dict[str, Any]) -> Dict[str, Any]:
        """Get data from volumeInfo"""
        info = book.get("volumeInfo", {})
        return {
            "title": info.get("title", NO_TITLE),
            "description": info.get("description", NO_DESCRIPTION),
            "authors": ", ".join(info.get("authors", [NO_AUTHORS])),
            "language": info.get("language", ""),
        }

    def filter_books(self, books: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out books with excluded language (ru)"""
        filtered = [
            book
            for book in books
            if self.extract_volume_info(book)["language"] != self.excluded_language
        ]
        logging.info(
            f"Filtered out {len(books) - len(filtered)} '{self.excluded_language}' books"
        )
        return filtered

    def safe_parse_float(self, value: str) -> Optional[float]:
        """Safely parse float from string. Returns None if parsing fails"""
        cleaned = value.strip().replace(" ", "").replace(",", ".")
        try:
            return float(re.match(r"[\d\.]+", cleaned).group())
        except Exception as e:
            logging.debug(f"safe_parse_float failed for '{value}': {e}")
            return None

    def parse_rating_from_html(self, html: str) -> Optional[float]:
        """Get rating from HTML"""
        try:
            soup = BeautifulSoup(html, "html.parser")
            for div in soup.find_all("div", class_="TT9eCd"):
                aria_label = div.get("aria-label", "")
                if aria_label and "Оцінка:" in aria_label:
                    match = re.search(r"Оцінка:\s*([\d\s,\.]+)", aria_label)
                    if match:
                        value = match.group(1)
                        val = self.safe_parse_float(value)
                        if val is not None:
                            return val
                text = div.text.strip().replace(",", ".")
                val = self.safe_parse_float(text)
                if val is not None:
                    return val
        except Exception as e:
            logging.exception(f"Exception when parsing HTML for rating: {e}")
        return None

    def format_for_tg(
        self, book: Dict[str, Any], rating: Union[float, str]
    ) -> Dict[str, Any]:
        """Format book info for sending to Telegram"""
        info = self.extract_volume_info(book)
        return {
            "title": info["title"],
            "description": info["description"],
            "authors": info["authors"],
            "rating": rating,
        }


def is_relevant(book_title: str, query: str, threshold: float = 0.7) -> bool:
    """Check if the book title is relevant to the query"""
    rel_title = book_title.lower()
    rel_query = query.lower().strip()
    ratio = SequenceMatcher(None, rel_title, rel_query).ratio()
    is_exact_substring = rel_query in rel_title
    return ratio >= threshold or is_exact_substring
