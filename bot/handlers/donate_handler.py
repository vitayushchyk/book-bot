from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from bot.handlers.cancel_handler import cancel_handler
from bot.handlers.start_handler import start

DONATE_CHOICE = 1

donate_link_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "На інфраструктуру та каву 🍻", url="https://donatello.to/HippobookSter"
            )
        ]
    ]
)

choice_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Го 🚀", callback_data="go_start"),
            InlineKeyboardButton("Пас 🙅‍♂️", callback_data="cancel_donate"),
        ]
    ]
)


async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        "`👀 Wanna support this  🦛💨?`\n" "`Тицяй 👇`\n",
        parse_mode="Markdown",
        reply_markup=donate_link_keyboard,
        disable_web_page_preview=True,
    )

    await update.message.reply_text(
        "Го продовжувати, чи ти пас? 🙂", reply_markup=choice_keyboard
    )
    return DONATE_CHOICE


async def donate_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "go_start":
        await start(update, context)
    elif query.data == "cancel_donate":
        await cancel_handler(update, context)
    return ConversationHandler.END


donate_handler = ConversationHandler(
    entry_points=[CommandHandler("donate", donate_command)],
    states={
        DONATE_CHOICE: [
            CallbackQueryHandler(donate_choice, pattern="^(go_start|cancel_donate)$")
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_handler),
    ],
)
