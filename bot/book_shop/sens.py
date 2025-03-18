from telegram.ext import ContextTypes

name_boor = range(1)

import logging


class Sens:
    def __init__(self, driver, sens_url):
        self.driver = driver
        self.sens_url = sens_url

    async def get_book(self, book_name):
        search_url_sens = f"{self.sens_url}{book_name}"
        self.driver.get(search_url_sens)

        try:
            books_data = self.driver.execute_script("return products;")
            if not books_data:
                logging.warning("No books found in the 'products' array.")
                return []
            normalized_query = " ".join(book_name.lower().strip().split())
            matching_books = []
            for book in books_data:
                title = book.get("title", "Назва відсутня")
                normalized_title = " ".join(title.lower().strip().split())
                if normalized_query in normalized_title:
                    matching_books.append(
                        {
                            "title": title,
                            "price": book.get("price", "Ціна відсутня"),
                            "link": book.get("url", "#"),
                        }
                    )
            if not matching_books:
                logging.warning(f"No books found matching the query: '{book_name}'.")
            return matching_books

        except Exception as e:
            logging.error(f"Error occurred while searching for books: {e}")
            return []
