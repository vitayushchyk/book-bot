import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.book_shop.bookling import Bookling

# from bot.book_shop.e_knygarnya import EKnygarnya
# from bot.book_shop.ksd import KSD
from bot.book_shop.readeat import Readeat
from bot.book_shop.sens import Sens
from bot.book_shop.yakaboo import Yakaboo

# from bot.book_shop.vivat import Vivat
# from bot.book_shop.yakaboo import Yakaboo
from bot.book_shop.zhupansky_publisher import ZhupanskyPublisher
from bot.core.config import settings
from bot.driver.chrome_driver import get_driver
from bot.handlers.shops_handler import (
    NAME_BOOK,
    book_name_handle,
    cancel_handler,
    start_search_book_handler,
)
from bot.handlers.start_handler import start
from bot.processor.search_manager import BookSearchManager

driver = get_driver()
logging.basicConfig()
logging.getLogger().setLevel(settings.get_log_level())


def get_app():
    logging.info("Initializing the bot...")
    try:
        yakaboo = Yakaboo(driver, settings.search_url_yakaboo)
        sens = Sens(driver, settings.search_url_sens)
        readeat = Readeat(driver, settings.search_url_readeat)
        # eknygarnya = EKnygarnya(driver, settings.search_url_eknygarnya)
        zhupansky = ZhupanskyPublisher(driver, settings.search_url_zhupansky)
        bookling = Bookling(driver, settings.search_url_bookling)
        # ksd = KSD(driver, settings.search_url_ksd)
        # vivat = Vivat(driver, settings.search_url_vivat)
        search_manager = BookSearchManager(
            [yakaboo, sens],
        )
        app = ApplicationBuilder().token(settings.bot_token).build()

        app.add_handler(CommandHandler("start", start))

        find_book_handler = ConversationHandler(
            entry_points=[
                CommandHandler(
                    "findbook",
                    lambda update, context: start_search_book_handler(
                        search_manager, update, context
                    ),
                ),
            ],
            states={
                NAME_BOOK: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        lambda update, context: book_name_handle(
                            search_manager, update, context
                        ),
                    )
                ],
            },
            fallbacks=[
                CommandHandler("cancel", cancel_handler),
            ],
        )
        app.add_handler(find_book_handler)

        logging.info("Bot initialized successfully.")
        app.run_polling()

    except Exception as e:
        logging.error(f"Error occurred while initializing the bot: {e}", exc_info=True)


if __name__ == "__main__":
    get_app()
