import logging

from selenium.webdriver.common.by import By

from bot.book_shop.base_shop import BaseShop
from bot.utils.book_details import get_book_details, get_book_details_from_element


class Readeat(BaseShop):
    async def get_book(self, book_name):
        search_url_readeat = f"{self.baseurl}{book_name}"

        self.driver.get(search_url_readeat)

        try:
            book_elements = self.driver.find_elements(By.CSS_SELECTOR, ".card-img-top")
            matching_books = []

            for book_element in book_elements:

                book_details = await get_book_details_from_element(
                    book_element, self.driver
                )
                if book_details:
                    raw_book_data = await get_book_details(book_details, "readeat")
                    if raw_book_data:
                        matching_books.append(raw_book_data)

            return matching_books
        except Exception as e:
            logging.error(f"Error loading books from readeat: {str(e)}")
            return []
