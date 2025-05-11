from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from states import WAITING_FOR_SEARCH_QUERY

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Поиск по базе":
        await update.message.reply_text("На какую тему найти веб-ресурсы?")
        return WAITING_FOR_SEARCH_QUERY

async def handle_search_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.delete()
    await update.message.reply_text(f"Вот веб-страницы на тему {query}")
    return ConversationHandler.END