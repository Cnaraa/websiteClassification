from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    keyboard = [["Поиск по базе"],
                ["Анализировать страницу"],
                ["Для разработчиков"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)