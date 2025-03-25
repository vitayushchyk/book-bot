import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Yakaboo:
    def __init__(self, driver, yakaboo_url: str):
        self.driver = driver
        self.yakaboo_url = yakaboo_url

    async def get_book(self, book_name: str):
        search_url_yakaboo = f"{self.yakaboo_url}/search?q={book_name.strip()}"
        self.driver.get(search_url_yakaboo)

        book_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.category-card")
        logging.info(
            f"Found {len(book_elements)} book cards for the query: {book_name}."
        )

        books = []
        for book in book_elements:
            try:
                title_element = book.find_element(By.CSS_SELECTOR, "a.ui-card-title")
                title = title_element.text.strip()
                url = title_element.get_attribute("href")

                price_element = book.find_element(
                    By.CSS_SELECTOR, "div.ui-price-display__main span"
                )
                price = price_element.text.strip()

                books.append(
                    {
                        "title": title,
                        "price": price,
                        "link": url,
                    }
                )
            except Exception as e:
                logging.error(f"Error while extracting book details: {e}")
                continue

        if not books:
            logging.warning(f"No books found for the query '{book_name}'.")
        return books
