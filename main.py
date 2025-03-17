import atexit
import logging

from telegram.ext import ApplicationBuilder, CommandHandler

from core.config import settings
from core.handlers.start_hendler import start
from core.sens import Sens
from driver.chrome_driver import get_driver

driver = get_driver()


def close_driver():
    logging.info("quit ChromeDriver...")
    driver.quit()


atexit.register(close_driver)

logging.basicConfig()
logging.getLogger().setLevel(settings.get_log_level())


def get_app():
    logging.info("Initializing the bot...")
    try:
        sens_url = "https://sens.in.ua/kataloh/search/?q="
        sens = Sens(driver, sens_url)

        app = ApplicationBuilder().token(settings.bot_token).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(
            CommandHandler(
                "findbook",
                lambda update, context: sens.get_book_handler(update, context),
            )
        )

        logging.info("Bot initialized successfully.")
        logging.info("Bot is running. Press Ctrl+C to stop.")
        app.run_polling()

    except Exception as e:
        logging.error("Error occurred while launching the bot: %s", e)


if __name__ == "__main__":
    get_app()
