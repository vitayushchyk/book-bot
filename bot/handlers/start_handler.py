import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.core.config import settings
from bot.servis.ratting_books import RattingBooks


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    await update.message.reply_text(
        f"`✨Йо, {user.first_name}✨`\n"
        f"`🧚 - твоя книжкова фея, створена - щоб знайти для тебе ідеальні пропозиції 🔥` \n\n"
        f"`Тут все, що моя розробниця навчила мене робити:🫦`\n\n"
        f"`🔹 Шукати книги по гарячим прайсам — тиць 👉` /findbook\n"
        f"`🔹 Передумав? Без драми — тиць 👉` /cancel\n",
        parse_mode="Markdown",
    )


google_books_client = RattingBooks(settings.google_book_api_key)


WAITING_FOR_BOOK_NAME = 1


async def book_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напишіть назву книги, яку хочете знайти у Google Books 📖:"
    )
    return WAITING_FOR_BOOK_NAME


async def infi_rating_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.warning("Test log: infi_rating_handler called")
    logging.info("Received a book name from user: %s", update.message.text)
    query = update.message.text.strip()

    result = google_books_client.search_book(query)
    logging.info(f"Received result from Google Books API: {result}")
    logging.info(f"Result: {result}")
    if result:
        message = (
            f"*Назва:* {result['title']}\n\n"
            f"*Автор:* {result['authors']}\n\n"
            f"*Опис:* {result['description']}\n\n"
            f"*Рейтинг:* {result['rating']}"
        )
    else:
        message = "Книгу не знайдено через Google Books 😔"
    await update.message.reply_text(message, parse_mode="Markdown")
