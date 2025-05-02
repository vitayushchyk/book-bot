import logging
from typing import List, Optional

import requests
from bs4 import BeautifulSoup


class SensBookParser:
    def __init__(self, baseurl: str):
        self.baseurl = baseurl

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.baseurl}{query.strip()}"
        logging.info(f"Fetching data from URL: {search_url}")

        try:
            response = requests.get(search_url, timeout=10)
            if response.status_code != 200:
                logging.error(
                    f"Failed to fetch page. Status code: {response.status_code}"
                )
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            books = self._parse_books(soup)
            logging.info(f"Successfully fetched {len(books)} books.")
            return books

        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP request error: {e}")
            return []

        except Exception as e:
            logging.error(f"Unexpected error while fetching books data: {e}")
            return []

    def _parse_books(self, soup: BeautifulSoup) -> List[dict]:

        books = []

        for card in soup.find_all("div", class_="catalogCard-main"):
            try:

                title = self._extract_text(card, "div", "catalogCard-title", "a")
                logging.info(f"Title: {title}")
                price = self._extract_text(card, "div", "catalogCard-price")
                logging.info(f"Price: {price}")
                link = self._extract_attribute(
                    card, "a", "href", parent_class="catalogCard-title"
                )
                logging.info(f"Link: {link}")

                books.append(
                    {
                        "title": title,
                        "price": price,
                        "url": f"https://sens.in.ua{link}" if link else None,
                    }
                )
                logging.info(
                    f"{ books.append({
                    "title": title,
                    "price": price,
                    "url": f"https://sens.in.ua{link}" if link else None  
                })}"
                )

            except AttributeError:
                logging.warning("Skipped a card due to missing data.")
                continue

        return books

    @staticmethod
    def _extract_text(
        card, parent_tag: str, parent_class: str, child_tag: Optional[str] = None
    ) -> Optional[str]:
        parent = card.find(parent_tag, class_=parent_class)
        if parent:
            if child_tag:
                child = parent.find(child_tag)
                return child.get_text(strip=True) if child else None
            return parent.get_text(strip=True)
        return None

    @staticmethod
    def _extract_attribute(
        card, tag: str, attr: str, parent_class: Optional[str] = None
    ) -> Optional[str]:
        parent = card.find("div", class_=parent_class) if parent_class else card
        if parent:
            element = parent.find(tag)
            if element and element.has_attr(attr):
                return element[attr]
        return None
