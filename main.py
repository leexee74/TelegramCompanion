import logging
import os
import sys
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    CallbackQueryHandler, ConversationHandler
)
from database import init_db
from handlers import (
    start, button_handler, text_handler, cancel,
    SUBSCRIPTION_CHECK, TOPIC, AUDIENCE, MONETIZATION,
    PRODUCT_DETAILS, PREFERENCES, STYLE, EMOTIONS,
    EXAMPLES, POST_NUMBER
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.error(f"============ ERROR OCCURRED ============")
    logger.error(f"Update: {update}")
    logger.error(f"Error: {context.error}")
    logger.error("========================================")

_updater = None

def run_telegram_bot():
    """Start the bot."""
    global _updater
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")

        # Initialize the bot
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            logger.error("Telegram bot token not found!")
            return

        # Create the Updater and pass it your bot's token
        _updater = Updater(token=TOKEN, use_context=True)
        dispatcher = _updater.dispatcher
        logger.info("Bot dispatcher initialized")

        # Add error handler
        dispatcher.add_error_handler(error_handler)
        logger.info("Error handler added")

        # Create conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                SUBSCRIPTION_CHECK: [
                    CallbackQueryHandler(button_handler, pattern='^check_subscription$')
                ],
                TOPIC: [
                    CallbackQueryHandler(button_handler, pattern='^start_work$'),
                    MessageHandler(Filters.text & ~Filters.command, text_handler)
                ],
                AUDIENCE: [
                    MessageHandler(Filters.text & ~Filters.command, text_handler)
                ],
                MONETIZATION: [
                    CallbackQueryHandler(button_handler, pattern='^(advertising|products|services|consulting)$')
                ],
                PRODUCT_DETAILS: [
                    MessageHandler(Filters.text & ~Filters.command, text_handler)
                ],
                PREFERENCES: [
                    MessageHandler(Filters.text & ~Filters.command, text_handler)
                ],
                STYLE: [
                    CallbackQueryHandler(button_handler, pattern='^(aggressive|business|humorous|custom)$'),
                    MessageHandler(Filters.text & ~Filters.command, text_handler)
                ],
                EMOTIONS: [
                    MessageHandler(Filters.text & ~Filters.command, text_handler)
                ],
                EXAMPLES: [
                    MessageHandler((Filters.text | Filters.forwarded) & ~Filters.command, text_handler),
                    CallbackQueryHandler(button_handler, pattern='^add_example$'),
                    CallbackQueryHandler(button_handler, pattern='^finish_examples$')
                ],
                POST_NUMBER: [
                    CallbackQueryHandler(button_handler, pattern='^new_plan$'),
                    MessageHandler(Filters.text & ~Filters.command, text_handler)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            allow_reentry=True,
            name="main_conversation"
        )

        # Add handler to dispatcher
        dispatcher.add_handler(conv_handler)
        logger.info("Conversation handler added")

        # Start the Bot without idle() to avoid signal handling issues
        logger.info("Bot starting...")
        _updater.start_polling(drop_pending_updates=True)
        logger.info("Bot started successfully!")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

def stop_telegram_bot():
    """Stop the bot if it's running."""
    global _updater
    if _updater is not None:
        try:
            logger.info("Stopping bot...")
            _updater.stop()
            _updater = None
            logger.info("Bot stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

if __name__ == '__main__':
    try:
        logger.info("Starting bot application...")
        run_telegram_bot()
    except Exception as e:
        logger.error("Critical error in main:", exc_info=True)
        sys.exit(1)