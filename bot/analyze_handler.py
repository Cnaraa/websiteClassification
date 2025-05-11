from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from get_html import get_html, create_driver
from parse_html import get_title_and_description
import re
import logging
from states import WAITING_FOR_URL
from classifier import classify_text


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if not re.match(r"^https?://", url):
        await update.message.reply_text("Введите корректную ссылку (начинающуюся с http или https).")
        return WAITING_FOR_URL

    try:
        await update.message.reply_text("Анализирую веб-страницу, это может занять несколько секунд...")

        driver = create_driver()
        html_content = get_html(driver, url)
        driver.quit()

        if html_content is None:
            await update.message.reply_text("Не удалось загрузить страницу.")
            return ConversationHandler.END

        title, description = get_title_and_description(html_content, url, query=None)
        if not title and not description:
            await update.message.reply_text("Не удалось найти заголовок или описание.")
            return ConversationHandler.END

        response = f"Заголовок: {title}\nОписание: {description}"

        try:
            predicted_category = classify_text(title=title, description=description)
            response += f"\nКатегория: {predicted_category}"
        except Exception as ex:
            logging.error(f"Ошибка при классификации текста: {ex}")
            response += "\nНе удалось определить категорию."

        await update.message.reply_text(response)

    except Exception as ex:
        logging.error(f"Ошибка при анализе страницы: {ex}")
        await update.message.reply_text("Произошла ошибка при анализе страницы.")

    return ConversationHandler.END