from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import GITHUB_LINK

async def handle_dev_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Для разработчиков":
        await update.message.reply_text(f"Ссылка для разработчиков: {GITHUB_LINK}")
        return ConversationHandler.END