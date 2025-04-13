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
        text="`✨Йо, шукач✨`\n"
        "`Введи назву книги, котру хочеш знайти 📚`\n"
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
        text=f"`Шукаю щось круте для тебе за запитом: '{book_name}' 🔍` \n"
        f"`Wait a sec, 🧚🏻‍ махає крилами, і це займає трохи часу`",
        parse_mode="Markdown",
    )
    try:

        books_info = await manager.fetch_books_from_all_libraries(book_name)

        if books_info:
            grouped_list = []
            grouped_books = {}

            for book in books_info:
                shop_name = book.get("shop", "Unknown")
                if shop_name not in grouped_books:
                    grouped_books[shop_name] = []
                grouped_books[shop_name].append(book)

            for shop_name, books in grouped_books.items():
                grouped_list.append({"shop": shop_name, "books": books})

            response = ""
            for group in grouped_list:
                shop_name = group["shop"]
                books = group["books"]

                response += f"`В кіоску: {shop_name.upper()}`\n\n"
                for book in books:
                    response += (
                        f"🔵 `Шо по назві?` {book.get('title', 'Гугл поламався')}\n"
                        f"🟡 `Шо по чом?` {book.get('price', 'Мабуть, безцінна')}\n"
                        f"[👉 Гоу за нею]({book.get('link', '#')})\n\n"
                    )

            if len(response) > 4000:

                parts = [response[i : i + 4000] for i in range(0, len(response), 4000)]
                for part in parts:
                    await update.message.reply_text(part, parse_mode="Markdown")
            else:

                await update.message.reply_text(response, parse_mode="Markdown")

        else:

            logging.warning(f"No books found for the query: '{book_name}'")
            await update.message.reply_text(
                text="`Воу-воу, стоПЕ`\n\n"
                f"`Книга з назвою` *'{book_name}'* `настільки ексклюзивна, що навіть гугл не знає 📚`\n\n"
                f"`Може, перевір правопис чи спробуй щось інше? 😉`",
                parse_mode="Markdown",
            )
    except Exception as e:
        logging.error(f"Error while handling the book search: {e}")
        await update.message.reply_text(
            text=f"`пу ПУ пу 🚨`\n\n"
            f"`Мабуть, розробниця переплутала код із чашкою капуча 🍺`\n"
            f"`Спробуй трохи пізніше 🙏`",
            parse_mode="Markdown",
        )

    await update.message.reply_text(
        text="`️Книжкова фея ще в ділі 🧚`\n\n"
        "`Від тебе — назва книги, від мене — пошук 🪄`\n"
        "`Якщо передумав — 👉` /cancel 🚪",
        parse_mode="Markdown",
    )
    return NAME_BOOK


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    logging.info("User canceled the book search.")
    await update.message.reply_text(
        text="`Охорона - відміна 👌`\n"
        f"`Якщо передумаєш — 🧚 завжди тут, як Wi-Fi сусіда 📡`",
        parse_mode="Markdown",
    )
    return ConversationHandler.END
