from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from parser import parse_page, save_to_db
from summarizer import summarize
from classifier import classify_text
from states import WAITING_FOR_URL
import logging

#Логирование
logging.basicConfig(
    filename="analyze_handler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.lower().startswith(("http://", "https://")):   
        await update.message.reply_text("Введите корректную ссылку (начинающуюся с http или https)")
        return ConversationHandler.END

    await update.message.reply_text("Анализируем сайт... Это может занять некоторое время.")

    result = parse_page(url, topic="unknown", save_to_db=False)
    if not result:
        await update.message.reply_text("Не удалось получить данные со страницы.")
        return ConversationHandler.END
    if result['topic'] != 'unknown':
        message = f"""
        URL: {url}
        Заголовок: {result['title']}
        Безопасность: {"HTTPS" if result['is_secure'] else "HTTP"}
        Описание: {result['description']}
        Краткая выжимка: {result['summary']}
        Тема: {result['topic']}"""
        await update.message.reply_html(message)
        return ConversationHandler.END

    title = result["title"]
    summary = result["summary"]

    try:
        predicted_category = classify_text(title=title, description=summary)
    except Exception as e:
        logging.error(f"Ошибка при классификации: {e}")
        predicted_category = "Не определено"

    result['topic'] = predicted_category
    save_to_db(result)

    message = f"""
    URL: {url}
    Заголовок: {result['title']}
    Безопасность: {"HTTPS" if result['is_secure'] else "HTTP"}
    Описание: {result['description']}
    Краткая выжимка: {result['summary']}
    Тема: {result['topic']}
    """
    await update.message.reply_html(message)

    return ConversationHandler.END 