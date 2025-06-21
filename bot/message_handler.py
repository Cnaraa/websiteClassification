from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from search_handler import handle_message as search_handle_message
from analyze_handler import handle_url
from dev_handler import handle_dev_message
from states import WAITING_FOR_SEARCH_QUERY, WAITING_FOR_URL

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Поиск по базе данных":
        return await search_handle_message(update, context)
    elif text == "Анализировать веб-страницу по URL":
        await update.message.reply_text("Введите ссылку на веб-страницу")
        return WAITING_FOR_URL
    elif text == "Получить информацию о модели":
        await handle_dev_message(update, context)
        return ConversationHandler.END