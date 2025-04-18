import logging

from bot.base.base_shop import BaseShop
from bot.utils.book_details import get_book_details


class Sens(BaseShop):
    async def get_book(self, book_name):
        search_url_sens = f"{self.baseurl}{book_name}"
        self.driver.get(search_url_sens)

        try:
            books_data = self.driver.execute_script("return products;")
            if not books_data:
                logging.warning("No books found in the 'products' array.")
                return []

            normalized_query = " ".join(book_name.lower().strip().split())
            matching_books = []

            for book in books_data:
                book_details = await get_book_details(book, source_type="sens")
                if book_details:
                    normalized_title = " ".join(
                        book_details["title"].lower().strip().split()
                    )
                    if normalized_query in normalized_title:
                        matching_books.append(book_details)

            if not matching_books:
                logging.info(
                    f"Found {len(matching_books)} matching books for query: '{book_name}'."
                )
            return matching_books

        except Exception as e:
            logging.error(f"Error occurred while searching for books: {e}")
            return []
