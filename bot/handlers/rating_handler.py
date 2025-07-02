import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.core.config import settings
from bot.servis.ratting_books import RattingBooks

GOOGLE_BOOKS_CLIENT = RattingBooks(settings.google_book_api_key)
WAITING_FOR_BOOK_NAME = 1


async def book_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"`Хай, хелло, {user.first_name}✨`\n\n"
        f"`Давай тайтл і 🦛💨 погнав сьорчити рейтинг`\n"
        f"`BTW, інглиш також можна юзати`",
        parse_mode="Markdown",
    )
    return WAITING_FOR_BOOK_NAME


async def infi_rating_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.warning("Test log: infi_rating_handler called")
    query = update.message.text.strip()
    result = await GOOGLE_BOOKS_CLIENT.search_book(query)
    if result:
        message = (
            f"📝 `Шо по назві? {result['title']}`\n\n"
            f"✍️ `Шо по автору?️️️️ ️{result['authors']}`\n\n"
            f"🎈 `Шо по опису? {result['description']}`\n\n"
            f"⭐️ `Шо по рейтингу? {result['rating']}`"
        )
    else:
        message = (
            f"`🤖 Воу, ну шо ви бачите перед собою, це ж СКАРБ '{query}'`\n"
            f"`API-шка зацінила, але такого не знайшла 😅`\n"
            f"`Погнав 🦛💨 upd робити, спробуй переможний try за іншим запитом`\n"
        )

    await update.message.reply_text(message, parse_mode="Markdown")
