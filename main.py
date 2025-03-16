import logging
import os
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, ConversationHandler
)
from handlers import start, button_handler, text_handler, cancel
from database import init_db
from utils import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def main():
    # Initialize the bot
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("Telegram bot token not found!")
        return

    # Initialize database
    init_db()

    # Create the Updater and pass it your bot's token.
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Define conversation states
    TOPIC, AUDIENCE, MONETIZATION, PRODUCT_DETAILS, PREFERENCES, STYLE, EMOTIONS, EXAMPLES = range(8)

    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TOPIC: [CallbackQueryHandler(button_handler), MessageHandler(Filters.text & ~Filters.command, text_handler)],
            AUDIENCE: [MessageHandler(Filters.text & ~Filters.command, text_handler)],
            MONETIZATION: [CallbackQueryHandler(button_handler)],
            PRODUCT_DETAILS: [MessageHandler(Filters.text & ~Filters.command, text_handler)],
            PREFERENCES: [MessageHandler(Filters.text & ~Filters.command, text_handler)],
            STYLE: [CallbackQueryHandler(button_handler)],
            EMOTIONS: [MessageHandler(Filters.text & ~Filters.command, text_handler)],
            EXAMPLES: [MessageHandler(Filters.text & ~Filters.command, text_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    logger.info("Bot starting...")
    updater.start_polling()
    logger.info("Bot started successfully!")
    updater.idle()

if __name__ == '__main__':
    main()