import logging
import os
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, ConversationHandler
)
from telegram.error import Conflict
from handlers import start, button_handler, text_handler, cancel
from database import init_db
from utils import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    if isinstance(context.error, Conflict):
        logger.error("Conflict error: Multiple bot instances detected")

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

    # Add error handler
    dispatcher.add_error_handler(error_handler)

    # Define conversation states
    TOPIC, AUDIENCE, MONETIZATION, PRODUCT_DETAILS, PREFERENCES, STYLE, EMOTIONS, EXAMPLES = range(8)

    # Create conversation handler with proper state management
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TOPIC: [
                CallbackQueryHandler(button_handler),
                MessageHandler(Filters.text & ~Filters.command, text_handler)
            ],
            AUDIENCE: [
                MessageHandler(Filters.text & ~Filters.command, text_handler)
            ],
            MONETIZATION: [
                CallbackQueryHandler(button_handler)
            ],
            PRODUCT_DETAILS: [
                MessageHandler(Filters.text & ~Filters.command, text_handler)
            ],
            PREFERENCES: [
                MessageHandler(Filters.text & ~Filters.command, text_handler)
            ],
            STYLE: [
                CallbackQueryHandler(button_handler),
                MessageHandler(Filters.text & ~Filters.command, text_handler)
            ],
            EMOTIONS: [
                MessageHandler(Filters.text & ~Filters.command, text_handler)
            ],
            EXAMPLES: [
                CallbackQueryHandler(button_handler),
                MessageHandler(Filters.text & ~Filters.command, text_handler)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    # Add handler to dispatcher
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    logger.info("Bot starting...")
    updater.start_polling()
    logger.info("Bot started successfully!")
    updater.idle()

if __name__ == '__main__':
    main()