from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    await update.message.reply_text(
        f"✨ *Йо, {user.first_name}!* ✨\n\n"
        "*Я твій книжковий маг* 🧙‍♂️, *створений, щоб знайти для тебе ідеальні пропозиції!* 🔥\n\n"
        "📚 _Тут усе, що моя розробниця навчила мене робити:_ 👇\n\n"
        "🔹 *Шукати книги за гарячими прайсами* — тиць 👉 /findbook\n"
        "🔹 *Передумав? Без драми* — тиць 👉 /cancel\n",
        parse_mode="Markdown",
    )
