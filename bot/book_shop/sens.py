# import logging
#
#
# class Sens:
#     def __init__(self, driver, sens_url):
#         self.driver = driver
#         self.sens_url = sens_url
#
#     async def get_book(self, book_name):
#         search_url_sens = f"{self.sens_url}{book_name}"
#         self.driver.get(search_url_sens)
#
#         try:
#             books_data = self.driver.execute_script("return products;")
#             if not books_data:
#                 logging.warning("No books found in the 'products' array.")
#                 return []
#             normalized_query = " ".join(book_name.lower().strip().split())
#             matching_books = []
#             for book in books_data:
#                 title = book.get("title", "Назва відсутня")
#                 normalized_title = " ".join(title.lower().strip().split())
#                 if normalized_query in normalized_title:
#                     matching_books.append(
#                         {
#                             "title": title,
#                             "price": book.get("price", "Ціна відсутня"),
#                             "link": book.get("url", "#"),
#                         }
#                     )
#             if not matching_books:
#                 logging.warning(
#                     f"No books found matching the query: '{book_name}'."
#                 )
#             return matching_books
#
#         except Exception as e:
#             logging.error(f"Error occurred while searching for books: {e}")
#             return []
#
#     async def get_book_handler(self, update, context):
#         if not context.args or len(context.args) == 0:
#             logging.info("No book name provided in the command.")
#             await update.message.reply_text(
#                 f"АЛАРМ, ти ж назву забув вказати після команди 😅"
#             )
#             return
#
#         book_name = " ".join(context.args)
#         logging.info(f"Received a request to search for books: {book_name}")
#         await update.message.reply_text(f"Шуршу архівами, щоб знайти книги, які містять у назві: {book_name}...")
#
#         try:
#             if books_info := await self.get_book(book_name):
#                 logging.info(f"Books found for the query: '{book_name}'")
#                 response = f"✅ Ось твої книги '{book_name}':\n\n"
#                 for book in books_info:
#                     response += (
#                         f"*Назва:* {book['title']}\n"
#                         f"*Ціна:* {book['price']}\n"
#                         f"[👉 тиць сюди]({book['link']})\n\n"
#                     )
#                 await update.message.reply_text(response, parse_mode="Markdown")
#             else:
#                 logging.warning(f"No books found for the query: '{book_name}'")
#                 await update.message.reply_text(
#                     f"❌ Жодної книги, яка містить '{book_name}' у назві, не знайдено."
#                 )
#         except Exception as e:
#             logging.error(f"Error while handling the request: {e}")
#             await update.message.reply_text(
#                 "❌ Сталася помилка під час пошуку книги. Спробуйте пізніше."
#             )

from telegram import Update
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
