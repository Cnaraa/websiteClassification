from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from semantic_search import search as semantic_search
from database import get_all_topics

from states import WAITING_FOR_SEARCH_QUERY

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Поиск по базе":
        await update.message.reply_text("Введите тему или ключевые слова:")
        return WAITING_FOR_SEARCH_QUERY

    return ConversationHandler.END


async def handle_search_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text.strip()
    await update.message.delete()

    await update.message.reply_text(f"Поиск по запросу: «{user_query}»")

    from semantic_search import load_all_articles, build_embeddings, search
    articles = load_all_articles()
    if not articles:
        await update.message.reply_text("База данных пустая. Сначала соберите данные.")
        return ConversationHandler.END

    _, embeddings = build_embeddings(articles)
    results = search(user_query, articles, embeddings)

    if not results:
        await update.message.reply_text("Ничего не найдено по вашему запросу.")
        return ConversationHandler.END

    for res in results:
        msg = f"""
<b>{res['title']}</b>
{res['url']}
{res['description'][:100]}...
Тема: {res['topic']}
        """
        await update.message.reply_html(msg)

    return ConversationHandler.END