import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from bot.book_shop.base_shop import BaseShop
from bot.utils.book_details import get_book_details


class Yakaboo(BaseShop):
    async def get_book(self, book_name: str) -> list:

        search_url_yakaboo = f"{self.baseurl}/search?q={book_name.strip()}"
        try:
            self.driver.get(search_url_yakaboo)
            book_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "div.category-card"
            )

            if not book_elements:
                logging.warning(
                    f"No books found for the query '{book_name}' on Yakaboo."
                )
                return []

            books = []
            filter_titles = set()

            for book in book_elements:
                try:
                    book_details = await get_book_details(book, source_type="yakaboo")
                    if book_details and book_details["title"] not in filter_titles:
                        books.append(book_details)
                        filter_titles.add(book_details["title"])

                except Exception as e:
                    logging.error(f"Error while extracting book details: {e}")
                    continue

            return books

        except (TimeoutException, NoSuchElementException) as ex:
            logging.error(f"Error fetching books on Yakaboo: {ex}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error while processing Yakaboo books: {e}")
            return []
