from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.core.config import settings
from bot.servis.ratting_books import RattingBooks

GOOGLE_BOOKS_CLIENT = RattingBooks(settings.google_book_api_key)
WAITING_FOR_BOOK_NAME = 1


async def book_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"`Хай, хелло, {user.first_name}✨`\n\n"
        f"`Давай тайтл і 🦛💨 погнав сьорчити рейтинг`\n"
        f"`BTW, інглиш також можна юзати 💁‍♀️`",
        parse_mode="Markdown",
    )
    return WAITING_FOR_BOOK_NAME


async def infi_rating_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
            f"`Воу, ну шо ви бачите перед собою,\n"
            f"це ж СКАРБ: '{query}' 🤖`\n"
            f"`API-шка зацінила, але такого не знайшла 💦`\n"
            f"`Погнав 🦛💨 upd робити`\n"
        )

    await update.message.reply_text(message, parse_mode="Markdown")
    await update.message.reply_text(
        f"`Го далі переможні траї робити та рейтинги сьорчити?🫡\n"
        f"Якщо ж ні - тицяй 👉`/cancel",
        parse_mode="Markdown",
    )


async def cancel_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "`Давай по новом, Міша, всьо х#$! 🤡👉`/start ", parse_mode="Markdown"
    )
    return ConversationHandler.END


rating_handler = ConversationHandler(
    entry_points=[CommandHandler("rating", book_rating)],
    states={
        WAITING_FOR_BOOK_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, infi_rating_handler)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_rating)],
)
