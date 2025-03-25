import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.book_shop.search_manager import BookSearchManager

NAME_BOOK = range(1)


async def start_search_book_handler(
    manager: BookSearchManager,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE = None,
):
    logging.info("Starting the book search interaction.")
    await update.message.reply_text(
        "`✨Йо, шукач✨`\n"
        "`Введи назву книги, котру хочеш знайти 📚`\n"
        "`BTW, якщо не шариш назву - шукай за автором ✍️`\n\n"
        "`Якщо передумав - тільки без драми 👉` /cancel 🚪",
        parse_mode="Markdown",
    )
    return NAME_BOOK


async def book_name_handle(
    manager: BookSearchManager,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE = None,
):
    book_name = update.message.text
    logging.info(f"Received a book name from user: {book_name}")
    await update.message.reply_text(
        f"`Шукаю щось круте для тебе за запитом: '{book_name} 🔍'` \n"
        f"`Це займе трохи часу, поки магічний пилок почне працювати💨🧚🏻‍♀️`",
        parse_mode="Markdown",
    )

    try:
        books_info = await manager.fetch_books_from_all_libraries(book_name)

        if books_info:
            logging.info(f"Books found for the query: '{book_name}'")
            response = (
                f"`Готуй свої money 💰`\n"
                f"`Ось що я 🧚 знайшла для` *'{book_name}'*:\n\n"
            )
            current_message = response
            messages = []

            for book in books_info:
                book_info = (
                    f"🔵 `Назва:` {book['title']}\n"
                    f"🟡 `Ціна:` {book['price']}\n"
                    f"[👉 Зазирни сюди]({book['link']})\n\n"
                )
                if len(current_message) + len(book_info) > 4000:
                    messages.append(current_message)
                    current_message = response + book_info
                else:
                    current_message += book_info

            if current_message:
                messages.append(current_message)

            for message in messages:
                await update.message.reply_text(message, parse_mode="Markdown")

        else:
            logging.warning(f"No books found for the query: '{book_name}'")
            await update.message.reply_text(
                f"`Воу-воу, стоПЕ`\n\n"
                f"`Книга з назвою` *'{book_name}'* `настільки ексклюзивна, що навіть бібліотеки такої не знають! 📚`\n\n"
                f"`Може, перевір правопис чи спробуй щось інше? 😉`",
                parse_mode="Markdown",
            )
    except Exception as e:
        logging.error(f"Error while handling the book search: {e}")
        await update.message.reply_text(
            f"`пу ПУ пу 🚨` \n\n"
            f"`Мабуть, розробниця переплутала код із чашкою капуча 🍺`\n"
            f"`Спробуй трохи пізніше 🙏`",
            parse_mode="Markdown",
        )

    await update.message.reply_text(
        "`️Книжкова фея ще в ділі 🧚`\n\n"
        "`Від тебе — назва книги, від мене — пошук 🪄`\n"
        "`Якщо передумав — 👉` /cancel 🚪",
        parse_mode="Markdown",
    )
    return NAME_BOOK


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    logging.info("User canceled the book search.")
    await update.message.reply_text(
        f"`Охорона - відміна 👌`\n"
        f"`Якщо передумаєш — я завжди тут, як Wi-Fi сусіда 📡`",
        parse_mode="Markdown",
    )
    return ConversationHandler.END
