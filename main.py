from app import app
import logging
import os
import sys
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    CallbackQueryHandler, ConversationHandler
)
from database import init_db
from handlers import (
    start, handle_main_menu, handle_repackage, button_handler, text_handler, cancel,
    SUBSCRIPTION_CHECK, MAIN_MENU, TOPIC, AUDIENCE, MONETIZATION,
    PRODUCT_DETAILS, PREFERENCES, STYLE, EMOTIONS,
    EXAMPLES, POST_NUMBER, REPACKAGE_AUDIENCE, REPACKAGE_TOOL, REPACKAGE_RESULT
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

def run_telegram_bot():
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

        # Create the Updater and pass it your bot's token
        updater = Updater(token=TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        logger.info("Bot dispatcher initialized")

        # Add error handler
        dispatcher.add_error_handler(error_handler)
        logger.info("Error handler added")

        # Create conversation handler with the new states
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                SUBSCRIPTION_CHECK: [
                    CallbackQueryHandler(button_handler, pattern='^check_subscription$')
                ],
                MAIN_MENU: [
                    CallbackQueryHandler(handle_main_menu)
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
                # New states for product repackaging
                REPACKAGE_AUDIENCE: [
                    MessageHandler(Filters.text & ~Filters.command, handle_repackage)
                ],
                REPACKAGE_TOOL: [
                    MessageHandler(Filters.text & ~Filters.command, handle_repackage)
                ],
                REPACKAGE_RESULT: [
                    MessageHandler(Filters.text & ~Filters.command, handle_repackage)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            allow_reentry=True,
            name="main_conversation"
        )

        # Add handler to dispatcher
        dispatcher.add_handler(conv_handler)
        logger.info("Conversation handler added")

        # Start the Bot
        logger.info("Bot starting...")
        updater.start_polling(drop_pending_updates=True)
        logger.info("Bot started successfully!")

        # Keep the bot running
        updater.idle()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        logger.info("Starting bot application...")
        run_telegram_bot()
    except Exception as e:
        logger.error("Critical error in main:", exc_info=True)
        sys.exit(1)