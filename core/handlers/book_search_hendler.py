from telegram import Update
from telegram.ext import ContextTypes

from core.config import settings
from core.sens import Sens
from driver.chrome_driver import get_driver

driver = get_driver()

import logging

from telegram import Update
from telegram.ext import ContextTypes

from driver.chrome_driver import get_driver

driver = get_driver()


async def get_book_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        logging.warning("No message object found in the update. Cannot reply.")
        return
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "Будь ласка, вкажіть назву книги після команди!"
        )
        return

    book_name = " ".join(context.args)
    logging.info(f"Отримано запит на пошук книг: {book_name}")
    await update.message.reply_text(f"Шукаю книги, які містять у назві: {book_name}...")
    sens_instance = Sens(driver, sens_url=settings.sens_url)

    try:
        books_info = await sens_instance.get_book(book_name)
    except Exception as e:
        logging.error(f"Error while fetching books: {e}")
        await update.message.reply_text(
            "❌ Сталася помилка під час пошуку книги. Спробуйте пізніше."
        )
        return

    try:
        books_info = await sens_instance.get_book(book_name)
    except Exception as e:
        logging.error(f"Error while fetching books: {e}")
        await update.message.reply_text(
            "❌ Сталася помилка під час пошуку книги. Спробуйте пізніше."
        )
        return

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
