import logging
from contextlib import asynccontextmanager

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.core.config import settings
from bot.handlers.cancel_handler import cancel_handler
from bot.handlers.donate_handler import donate_handler
from bot.handlers.rating_handler import rating_handler
from bot.handlers.shops_handler import (
    NAME_BOOK,
    book_name_handle,
    start_search_book_handler,
)
from bot.handlers.start_handler import start
from bot.handlers.user_comment_handler import comment_handler
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
from bot.processor.search_manager import BookSearchManager
from routers.health_check_routers import health_check_router
from routers.webhook_routers import webhook_router

logging.basicConfig()
logging.getLogger().setLevel(settings.get_log_level())

import logging

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app):
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
        [
            yakaboo,
            sens,
            readeat,
            eknygarnya,
            zhupansky,
            bookling,
            ksd,
            vivat,
            lion,
            mbooks,
            fabula,
        ]
    )

    telegram_application = (
        ApplicationBuilder().token(settings.bot_token).concurrent_updates(True).build()
    )

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
            CommandHandler("start", start),
        ],
    )
    telegram_application.add_handler(rating_handler)
    telegram_application.add_handler(comment_handler)
    telegram_application.add_handler(find_book_handler)
    telegram_application.add_handler(donate_handler)
    telegram_application.add_handler(CommandHandler("start", start))

    await telegram_application.initialize()
    await telegram_application.start()

    webhook_url = settings.webhook_url
    try:
        success = await telegram_application.bot.set_webhook(webhook_url)
        if success:
            logging.info(f"Webhook set to: {webhook_url}")
        else:
            logging.error("Failed to set webhook.")
    except Exception as e:
        logging.exception(f"Error setting webhook: {e}")

    app.state.telegram_application = telegram_application
    app.state.search_manager = search_manager
    try:
        yield
    finally:
        telegram_application = app.state.telegram_application
        await telegram_application.stop()
        await telegram_application.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(health_check_router)
app.include_router(webhook_router)
