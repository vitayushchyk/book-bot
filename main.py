import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.core.config import settings
from bot.core.shops_config import MANAGER_CONFIGS
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
from bot.processor.search_manager import BookSearchManager
from bot.routers.health_check_routers import health_check_router
from bot.routers.webhook_routers import webhook_router

logging.basicConfig()
logging.getLogger().setLevel(settings.get_log_level())


@asynccontextmanager
async def lifespan(app):
    managers = [cls(url) for cls, url in MANAGER_CONFIGS]
    search_manager = BookSearchManager(managers)

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
    handlers = [
        rating_handler,
        comment_handler,
        find_book_handler,
        donate_handler,
        CommandHandler("start", start),
    ]
    for handler in handlers:
        telegram_application.add_handler(handler)

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
