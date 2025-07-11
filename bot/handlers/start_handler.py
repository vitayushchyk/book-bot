from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    await update.message.reply_text(
        f"`✨Йо, {user.first_name}✨`\n"
        f"`🦛💨 - Hippo bookSter, створений - щоб знайти для тебе ідеальні пропозиції 🔥` \n\n"
        f"`Тут все, що моя розробниця навчила мене робити 🫦`\n\n"
        f"`🔹 Шукати книги по гарячим прайсам — тиць 👉` /findbook\n"
        f"`🔹 Шукати рейтинг книги — тиць 👉` /rating\n"
        f"`🔹 Писати хороші і погані слова тиць 👉` /comment"
        f"`🔹 Передумав? Без драми — тиць 👉` /cancel\n",
        parse_mode="Markdown",
    )
