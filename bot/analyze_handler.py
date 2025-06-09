from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from parser import parse_url
from summarizer import summarize
from classifier import classify_text
from states import WAITING_FOR_URL

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    #Проверка корректности URL
    if not url.startswith("http"):
        await update.message.reply_text("Введите корректную ссылку (начинающуюся с http или https)")
        return ConversationHandler.END

    await update.message.reply_text("Анализируем сайт... Это может занять несколько секунд.")

    #Парсинг сайта через parser.py
    topic = "unknown"
    article_data = parse_url(url, topic)

    if not article_data:
        await update.message.reply_text("Не удалось получить данные со страницы.")
        return ConversationHandler.END

    full_text = article_data["full_text"]
    title = article_data["title"]
    description = article_data["description"]
    is_secure = article_data["is_secure"]

    #Проверка на пустой или ошибочный контент
    if len(full_text) < 10 or any(kw in full_text.lower() for kw in ["404", "не найдена", "ошибка"]):
        await update.message.reply_text("Страница не существует или содержит ошибку (например, 404).")
        return ConversationHandler.END

    #Суммаризация
    try:
        summary = summarize(full_text)
    except Exception as e:
        logging.error(f"Ошибка при суммаризации: {e}")
        summary = "Не удалось сгенерировать выжимку"

    #Классификация
    try:
        predicted_category = classify_text(title=title, description=summary)
    except Exception as e:
        logging.error(f"Ошибка при классификации: {e}")
        predicted_category = "Не определено"

    #Сохраняем в БД
    from database import save_to_db
    article_data["summary"] = summary
    article_data["topic"] = predicted_category
    save_to_db(article_data)

    #Ответ пользователю
    message = f"""
URL: {url}
Заголовок: {title}
Безопасность: {"HTTPS" if is_secure else "HTTP"}
Описание: {description[:150]}...
Краткая выжимка: {summary[:200]}...
Тема: {predicted_category}
    """

    await update.message.reply_html(message)
    return ConversationHandler.END