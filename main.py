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

# Set up logging with more details
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
    logger.error('Update "%s" caused error "%s"', update, context.error, exc_info=True)

def main():
    """Start the bot."""
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")

        # Initialize the bot
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            logger.error("Telegram bot token not found!")
            return

        # Log token validation (without exposing the actual token)
        logger.info(f"Token loaded, length: {len(TOKEN)}")
        logger.info("Initializing bot with token...")

        # Create the Updater and pass it your bot's token
        updater = Updater(token=TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        logger.info("Bot dispatcher initialized")

        # Verify bot identity
        me = updater.bot.get_me()
        logger.info(f"Bot identity verified: @{me.username}")

        # Add error handler first
        dispatcher.add_error_handler(error_handler)
        logger.info("Error handler added")

        # Create conversation handler with proper state management
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
                    MessageHandler(Filters.text & ~Filters.command, text_handler),
                    CallbackQueryHandler(button_handler, pattern='^add_example$'),
                    CallbackQueryHandler(button_handler, pattern='^finish_examples$')
                ],
                POST_NUMBER: [
                    CallbackQueryHandler(button_handler, pattern='^new_plan$'),
                    MessageHandler(Filters.text & ~Filters.command, text_handler)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            allow_reentry=True
        )

        # Add handler to dispatcher
        dispatcher.add_handler(conv_handler)
        logger.info("Conversation handler added")

        # Start the Bot with drop_pending_updates to avoid conflicts
        logger.info("Bot starting...")
        logger.info("Initializing polling...")
        updater.start_polling(drop_pending_updates=True)
        logger.info("Bot started successfully!")
        logger.info("Long polling started, waiting for messages...")

        # Keep the bot running
        updater.idle()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        logger.info("Starting bot application...")
        main()
    except Exception as e:
        logger.error("Critical error in main:", exc_info=True)
        sys.exit(1)