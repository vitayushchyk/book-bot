import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from bot.book_shop.base_shop import BaseShop


class Yakaboo(BaseShop):

    async def get_book(self, book_name: str):
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

            logging.info(
                f"Found {len(book_elements)} book cards for the query '{book_name}'."
            )

            books = []
            for book in book_elements:
                try:

                    book_details = self._get_book_details(book)
                    if book_details:
                        books.append(book_details)
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

    def _get_book_details(self, book):
        try:

            title_element = book.find_element(By.CSS_SELECTOR, "a.ui-card-title")
            title = title_element.text.strip()
            link = title_element.get_attribute("href")

            price_element = book.find_element(
                By.CSS_SELECTOR, "div.ui-price-display__main span"
            )
            price = (
                price_element.text.strip() if price_element else "Price not available"
            )

            return {
                "title": title,
                "price": price,
                "link": link,
            }

        except NoSuchElementException as e:
            logging.error(f"Failed to locate book details in card: {e}")
            return None
