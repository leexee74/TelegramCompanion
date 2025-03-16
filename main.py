import logging
import os
import signal
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, ConversationHandler
)
from telegram.error import Conflict, TelegramError
from handlers import (
    start, button_handler, text_handler, cancel,
    TOPIC, AUDIENCE, MONETIZATION, PRODUCT_DETAILS,
    PREFERENCES, STYLE, EMOTIONS, EXAMPLES, POST_NUMBER,
    SUBSCRIPTION_CHECK
)
from database import init_db
from utils import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def stop_bot(updater):
    """Stop the bot gracefully."""
    if updater:
        logger.info("Stopping bot...")
        updater.stop()
        updater.is_idle = False

def error_handler(update, context):
    """Log Errors caused by Updates."""
    if isinstance(context.error, Conflict):
        logger.error("Conflict error: Multiple bot instances detected")
        if hasattr(context, 'bot_data') and 'updater' in context.bot_data:
            stop_bot(context.bot_data['updater'])
    elif isinstance(context.error, TelegramError):
        logger.error(f"Telegram error: {context.error}")
    else:
        logger.error('Update "%s" caused error "%s"', update, context.error, exc_info=True)

def main():
    """Start the bot."""
    try:
        # Initialize the bot
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            logger.error("Telegram bot token not found!")
            return

        # Initialize database
        init_db()
        logger.info("Database initialized")

        # Create the Updater and pass it your bot's token
        updater = Updater(token=TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        logger.info("Bot dispatcher initialized")

        # Store updater in bot_data for access in error handler
        dispatcher.bot_data['updater'] = updater

        # Add error handler
        dispatcher.add_error_handler(error_handler)

        # Create conversation handler with proper state management
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                SUBSCRIPTION_CHECK: [
                    CallbackQueryHandler(button_handler)
                ],
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
                POST_NUMBER: [
                    MessageHandler(Filters.text & ~Filters.command, text_handler),
                    CallbackQueryHandler(button_handler)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            allow_reentry=True
        )

        # Add handler to dispatcher
        dispatcher.add_handler(conv_handler)
        logger.info("Conversation handler added to dispatcher")

        # Start the Bot with drop_pending_updates to avoid conflicts
        logger.info("Bot starting...")
        updater.start_polling(drop_pending_updates=True)
        logger.info("Bot started successfully!")

        # Handle graceful shutdown
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal")
            stop_bot(updater)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        updater.idle()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()