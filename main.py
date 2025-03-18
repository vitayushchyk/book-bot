import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.book_shop.sens import Sens
from bot.core.config import settings
from bot.driver.chrome_driver import get_driver
from bot.handlers.sens_handler import (
    NAME_BOOK,
    book_name_handle,
    cancel_handler,
    start_search_book_handler,
)
from bot.handlers.start_handler import start

driver = get_driver()
logging.basicConfig()
logging.getLogger().setLevel(settings.get_log_level())


def get_app():
    logging.info("Initializing the bot...")
    try:
        sens_url = settings.search_url_sens
        sens = Sens(driver, sens_url)

        app = ApplicationBuilder().token(settings.bot_token).build()

        app.add_handler(CommandHandler("start", start))

        find_book_handler = ConversationHandler(
            entry_points=[
                CommandHandler(
                    "findbook",
                    lambda update, context: start_search_book_handler(
                        sens, update, context
                    ),
                ),
            ],
            states={
                NAME_BOOK: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda update, context: book_name_handle(sens, update, context),
                    )
                ],
            },
            fallbacks=[
                CommandHandler("cancel", cancel_handler),
            ],
        )
        app.add_handler(find_book_handler)

        logging.info("Bot initialized successfully.")
        logging.info("Bot is running. Press Ctrl+C to stop.")
        app.run_polling()

    except Exception as e:
        logging.error(f"Error occurred while launching the bot: {e}", exc_info=True)


if __name__ == "__main__":
    get_app()
