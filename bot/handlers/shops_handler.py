import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.helpers import escape_markdown

from bot.processor.search_manager import BookSearchManager

NAME_BOOK = range(1)
MAX_MESSAGE_LENGTH = 4000


async def start_search_book_handler(
    manager: BookSearchManager,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE = None,
):
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

            cheapest_book = min(
                books_info,
                key=lambda x: (
                    float(x.get("price", "inf").split()[0])
                    if isinstance(x.get("price"), str)
                    and x.get("price").split()[0].isdigit()
                    else float("inf")
                ),
            )

            response_parts = []
            if cheapest_book:
                escaped_title = escape_markdown(
                    cheapest_book.get("title", "Гугл поламався"), version=2
                )
                escaped_price = escape_markdown(
                    cheapest_book.get("price", "Мабуть, безцінна"), version=2
                )
                escaped_link = cheapest_book.get("link", "#")
                escaped_shop = escape_markdown(
                    cheapest_book.get("shop", "").upper(), version=2
                )

                cheapest_book_response = (
                    f"`🔥 УРВАТЬ НАЙДЕШЕВШУ 🔥`\n\n"
                    f"🛒 `Де шукать?` {escaped_shop}\n"
                    f"💸 `Шо по чом?` {escaped_price}\n"
                    f"📝`Шо по назві?` {escaped_title}\n"
                    f"[🚀 Гоу за нею]({escaped_link})\n\n"
                    f"`🔵🟡🔵🟡🔵`\n\n"
                )
                response_parts.append(cheapest_book_response)

            current_response = ""

            for group in grouped_list:
                shop_name = group["shop"]
                books = group["books"]

                escaped_shop_name = escape_markdown(shop_name.upper(), version=2)
                shop_response = f"`В кіоску: - ✨{escaped_shop_name}✨`\n\n"

                for book in books:
                    escaped_title = escape_markdown(
                        book.get("title", "Гугл поламався"), version=2
                    )
                    escaped_price = escape_markdown(
                        book.get("price", "Мабуть, безцінна"), version=2
                    )
                    escaped_link = book.get("link", "#")

                    book_response = (
                        f"📝`Шо по назві?` {escaped_title}\n"
                        f"💸 `Шо по чом?` {escaped_price}\n"
                        f"[🚀 Гоу за нею]({escaped_link})\n\n"
                        f"`🔵🟡🔵🟡🔵`\n\n"
                    )

                    if (
                        len(current_response) + len(shop_response) + len(book_response)
                        > MAX_MESSAGE_LENGTH
                    ):
                        response_parts.append(current_response)
                        current_response = ""

                    if shop_response not in current_response:
                        current_response += shop_response
                    current_response += book_response

            if current_response:
                response_parts.append(current_response)

            for part in response_parts:
                await update.message.reply_text(part, parse_mode="MarkdownV2")
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
