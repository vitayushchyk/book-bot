import logging
from typing import List


class SensBookParser:
    def __init__(self, driver, baseurl: str):
        self.driver = driver
        self.baseurl = baseurl

    async def fetch_books_data(self, query: str) -> List[dict]:
        search_url = f"{self.baseurl}{query.strip()}"
        logging.info(f"Navigating to search URL: {search_url}")
        self.driver.get(search_url)

        try:
            books_data = self.driver.execute_script("return products;")
            if not books_data:
                logging.warning("No books found in the 'products' array.")
                return []
            logging.info(f"Found {len(books_data)} books in the 'products' array.")
            return books_data

        except Exception as e:
            logging.error(f"Error fetching book data: {e}")
            return []
