import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from telegram import Update
from telegram.ext import ContextTypes


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
                logging.warning("Жодних книг немає у масиві 'products'.")
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
                logging.warning(
                    f"Не знайдено книг, які відповідають запиту: '{book_name}'."
                )
            return matching_books

        except Exception as e:
            logging.error(f"Помилка під час пошуку книг: {e}")
            return []

    async def get_book_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if not context.args or len(context.args) == 0:
            await update.message.reply_text(
                "Будь ласка, вкажіть назву книги після команди!"
            )
            return

        book_name = " ".join(context.args)
        logging.info(f"Отримано запит на пошук книг: {book_name}")
        await update.message.reply_text(
            f"Шукаю книги, які містять у назві: {book_name}..."
        )

        books_info = await self.get_book(book_name)

        if books_info:
            response = f"✅ Знайдені книги за запитом '{book_name}':\n\n"
            for book in books_info:
                response += (
                    f"*Назва:* {book['title']}\n"
                    f"*Ціна:* {book['price']}\n"
                    f"[👉 тиць сюди]({book['link']})\n\n"
                )
            await update.message.reply_text(response, parse_mode="Markdown")
        else:
            await update.message.reply_text(
                f"❌ Жодної книги, яка містить '{book_name}' у назві, не знайдено."
            )
