from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.core.config import settings
from bot.servis.ratting_base import is_relevant
from bot.servis.ratting_books import RattingBooks

GOOGLE_BOOKS_CLIENT = RattingBooks(settings.google_book_api_key)
WAITING_FOR_BOOK_NAME = 1
NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]


async def book_rating(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        text=f"`Хай, хелло, {user.first_name}✨`\n\n"
        f"`Давай тайтл і 🦛💨 погнав сьорчити рейтинг`\n"
        f"`BTW, інглиш також можна юзати 💁‍♀️`",
        parse_mode="Markdown",
    )
    return WAITING_FOR_BOOK_NAME


async def infi_rating_handler(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    result = await GOOGLE_BOOKS_CLIENT.search_book(query)
    if result:
        relevant_books = [book for book in result if is_relevant(book["title"], query)]
        if not relevant_books:
            await update.message.reply_text(
                text=f"`no, no, no, фейл 😶‍🌫️`\n" "`maybe, інший запит 👀`",
                parse_mode="Markdown",
            )
        else:
            for idx, book in enumerate(relevant_books, 1):
                if idx <= len(NUMBER_EMOJIS):
                    num_str = NUMBER_EMOJIS[idx - 1]
                else:
                    num_str = f"{idx}"
                message = (
                    f"`Attention, oсь що маю для тебе 📖 number - {num_str}`\n\n"
                    f"📝 `{book['title']}`\n"
                    f"✍️ `{book['authors']}`\n"
                    f"🎈 `{book['description']}`\n"
                    f"⭐️ `{book['rating']}`"
                )
                await update.message.reply_text(message, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            text=(
                "`Воу, шо ви бачите перед собою,\n"
                f"це ж СКАРБ: '{query}' 🤖`\n"
                "`API-шка зацінила, але такого не знайшла 💦`\n"
                "`Погнав 🦛💨 upd робити`\n"
            ),
            parse_mode="Markdown",
        )
    await update.message.reply_text(
        text=(
            "`Го далі переможні траї робити та рейтинги сьорчити?🫡\n"
            "Якщо ж ні - тицяй 👉`/cancel"
        ),
        parse_mode="Markdown",
    )


async def cancel_rating(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="`Давай по новом, Міша, всьо х#$! 🤡👉`/start ", parse_mode="Markdown"
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
