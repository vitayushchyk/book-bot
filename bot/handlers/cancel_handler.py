import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.helpers import escape_markdown


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    logging.info("User canceled the book search.")
    await update.message.reply_text(
        text="`ОХРАНА - ОТМЄНА 👌`\n\n"
        f"`Передумав?\n"
        f"Пінгуй, 🦛💨 завжди тут, як Wi-Fi сусіда 📡`  👉 /start",
        parse_mode="Markdown",
    )
    return ConversationHandler.END
