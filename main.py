import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from websocket import frame_buffer

from bot.core.config import settings
from bot.handlers.shops_handler import (
    NAME_BOOK,
    book_name_handle,
    cancel_handler,
    start_search_book_handler,
)
from bot.handlers.start_handler import start
from bot.manager.bookling import Bookling
from bot.manager.e_knygarnya import EKnygarnya
from bot.manager.fabula import Fabula
from bot.manager.ksd import KSD
from bot.manager.mbooks import MegogoBooks
from bot.manager.old_lion import OldLion
from bot.manager.readeat import Readeat
from bot.manager.sens import Sens
from bot.manager.vivat import Vivat
from bot.manager.yakaboo import Yakaboo
from bot.manager.zhupansky_publisher import ZhupanskyPublisher
from bot.parser.fabula_parser import FabulaParser
from bot.parser.mbooks_parser import MegogoBooksParser
from bot.processor.search_manager import BookSearchManager

logging.basicConfig()
logging.getLogger().setLevel(settings.get_log_level())


def get_app():
    logging.info("Initializing the bot...")
    try:
        yakaboo = Yakaboo(settings.search_url_yakaboo)
        sens = Sens(settings.search_url_sens)
        readeat = Readeat(settings.search_api_url_readeat)
        eknygarnya = EKnygarnya(settings.search_url_eknygarnya)
        zhupansky = ZhupanskyPublisher(settings.search_url_zhupansky)
        bookling = Bookling(settings.search_url_bookling)
        ksd = KSD(settings.search_url_ksd)
        vivat = Vivat(settings.search_url_vivat)
        lion = OldLion(settings.search_url_old_lion)
        mbooks = MegogoBooks(settings.search_url_mbooks)
        fabula = Fabula(settings.search_url_fabula)
        search_manager = BookSearchManager(
            [readeat],
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
