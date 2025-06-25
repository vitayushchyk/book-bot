import json
import logging
from typing import Any, List, Optional
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from bot.base.base_fetch_page_mixin import FetchPageMixin


class BaseParser:
    def __init__(self, base_url=None, api_url=None, params=None):
        self.base_url = base_url
        self.api_url = api_url
        self.search_params = params

    async def build_search_url(self, query: str) -> str:
        """Build the search URL for the given query"""
        url_base = self.api_url or self.base_url
        params = self.search_params.copy() if self.search_params else None

        try:
            if params is not None:
                params["s"] = query
                query_string = urlencode(params)
                url = f"{url_base}?{query_string}"
            else:
                url = f"{url_base}{query.strip()}"

            logging.info(
                f"[{self.__class__.__name__}] Built search URL: {url!r} for query: {query!r}"
            )
            return url

        except Exception as e:
            logging.error(
                msg=f"[{self.__class__.__name__}] Error building search URL for query {query!r}: {e}",
                exc_info=True,
            )
            raise

    async def fetch_page(self, url: str):
        """Fetch the page content from the given URL"""
        try:
            res_txt = await FetchPageMixin.fetch_page(url)
            logging.info(f"[{self.__class__.__name__}] Fetched page: {url!r}")
            if not res_txt:
                return []
            return res_txt
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}] Error fetching page: {e}")
            return []

    @staticmethod
    async def _parse_json(response_text: Optional[str]) -> Optional[dict]:
        """Parse the JSON response text"""
        if response_text is None:
            return None
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from response text.")
            return None

    async def parse_html_use_soup(self, html_text: str) -> BeautifulSoup:
        """Parse the HTML response text using BeautifulSoup"""
        result = BeautifulSoup(html_text, features="html.parser")
        logging.info(
            f"[Successfully parsed HTML using BeautifulSoup in {self.__class__.__name__}]"
        )

        return result

    @staticmethod
    def _add_book(item: dict, books: list):
        title = item.get("name")
        price = item.get("price")
        url = item.get("url")
        if title:
            books.append(
                {
                    "title": title,
                    "price": price,
                    "url": url,
                }
            )
