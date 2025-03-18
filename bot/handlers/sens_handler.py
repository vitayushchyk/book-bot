import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

NAME_BOOK = range(1)


async def start_search_book_handler(
    sens, update: Update, context: ContextTypes.DEFAULT_TYPE = None
):
    logging.info("Starting the book search interaction.")
    await update.message.reply_text(
        "✨*Йо, шукач!*✨\n"
        "Введи назву книги, яку шукаєш 📚\n"
        "Якщо передумав — 👉 /cancel 🚪",
        parse_mode="Markdown",
    )
    return NAME_BOOK


async def book_name_handle(
    sens, update: Update, context: ContextTypes.DEFAULT_TYPE = None
):
    book_name = update.message.text
    logging.info(f"Received a book name from user: {book_name}")
    await update.message.reply_text(
        f"Шукаю щось круте для тебе за запитом: *'{book_name}'*! 🔍📚",
        parse_mode="Markdown",
    )

    try:
        if books_info := await sens.get_book(book_name):
            logging.info(f"Books found for the query: '{book_name}'")
            response = (
                f"📚 *Готуй свої money!* Ось що я 🧙 знайшов для *'{book_name}'*:\n\n"
            )
            for book in books_info:
                response += (
                    f"🔵 *Назва:* {book['title']}\n"
                    f"🟡 *Ціна:* {book['price']}\n"
                    f"[👉 Зазирни сюди]({book['link']})\n\n"
                )
            await update.message.reply_text(response, parse_mode="Markdown")
        else:
            logging.warning(f"No books found for the query: '{book_name}'")
            await update.message.reply_text(
                f"😕 _Воу-воу, стоПЕ!_ \n\n"
                f"Книга з назвою *'{book_name}'* настільки ексклюзивна, що навіть бібліотеки такої не знають! 📚\n\n"
                f"Може, перевір правопис чи спробуй щось інше? 😉",
                parse_mode="Markdown",
            )
    except Exception as e:
        logging.error(f"Error while handling the book search: {e}")
        await update.message.reply_text(
            "🚨 *пу ПУ пу!* \n\n"
            "_Мабуть, розробниця переплутала код із чашкою капуча._ ☕\n\n"
            "Спробуй трохи пізніше! 🙏",
            parse_mode="Markdown",
        )
    await update.message.reply_text(
        "🧙‍♂️ *Книжковий маг ще в ділі!*\n\n"
        "Від тебе — _назва книги_, від мене — *пошук*. Якщо передумав — 👉 /cancel 🚪",
        parse_mode="Markdown",
    )
    return NAME_BOOK


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    logging.info("User canceled the book search.")
    await update.message.reply_text(
        "✅ *Окей, пошук відмінено!*\n\n"
        "Якщо передумаєш — просто скажи, *я завжди тут, як Wi-Fi сусіда* 📡",
        parse_mode="Markdown",
    )
    return ConversationHandler.END
