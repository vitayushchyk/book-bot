from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.db.conection import get_session
from bot.db.user_comment import UserComment
from bot.handlers.cancel_handler import cancel_handler

GET_COMMENT = 1


async def comment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"`Мяуу, нашкрябай фітбек знизу 👇`\n\n"
        f"`Рандомний інсайт, баг чи просто соул біль? 🌚`\n"
        f"`Кидай, не тримай в собі 🫦`\n"
        f"`Від тебе — текст, від 🦛💨 — рандомний вайб`\n"
        f"`і делівері прямо dev'чині 💌`\n"
        f"`Хай таски робить, а не капуч 🍻 п'є, АУФФ 🐺☝️ `",
        parse_mode="Markdown",
    )
    return GET_COMMENT


async def save_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    comment_text = update.message.text

    user_display_name = user.username if user.username else user.first_name

    async with get_session() as session:
        comment = UserComment(username=user_display_name, comment=comment_text)
        session.add(comment)
        await session.commit()

    await update.message.reply_text(
        f"`РАХУЄТЬСЯ! Дякую, ціную дуже, {user.first_name}! 💙💛`\n\n"
        f"`Апдейти, меми і покращення вже НЕЗАБАРОМ 💅`\n"
        f"`P.S. Щастя, здоровля, не забувай донати на ЗСУ 🇺🇦️‍🍩`\n"
        f"`Тицяй, якщо ще маєш справи до 🦛💨` /start",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


comment_handler = ConversationHandler(
    entry_points=[CommandHandler("comment", comment_command)],
    states={
        GET_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_comment)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_handler),
    ],
)
