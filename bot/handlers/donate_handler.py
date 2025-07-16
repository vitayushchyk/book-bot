import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)


async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "`Wanna support this 👀`\n\n"
        "`Твої 🍩 — це заряд 💸 наших серверів`\n"
        "`Та дріпчики 🍻 для dev'чині`\n"
        "`Тицяй на лінку для енергообміну 💕✨`\n"
        "[Donatello](https://donatello.to/HippobookSter)\n\n"
        "`Ми вері дякуємо 🦛💨🥺`",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

    await asyncio.sleep(10)

    await update.message.reply_text(
        "`Летс гоу — 👻 `/start\n" "`Скіпаєшся вже — 🙅` /cancel\n",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


donate_handler = CommandHandler("donate", donate_command)
