# start_handler.py

from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Привіт, {user.first_name}! Я ваш помічник у пошуку книг 😊.\n"
        "Введіть назву книги, яка вас цікавить, і я спробую знайти вигідні пропозиції!"
    )
