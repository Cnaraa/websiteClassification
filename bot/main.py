from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from start_handler import start
from search_handler import handle_search_query, handle_message as search_handle_message
from analyze_handler import handle_url
from message_handler import handle_message
from dev_handler import handle_dev_message
from config import TOKEN
from states import WAITING_FOR_SEARCH_QUERY, WAITING_FOR_URL
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        states={
            WAITING_FOR_SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_query)],
            WAITING_FOR_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()