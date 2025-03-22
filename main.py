import logging
import os
import sys
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    CallbackQueryHandler, ConversationHandler
)
from handlers import (
    start, button_handler, handle_main_menu, cancel,
    handle_repackage_audience, handle_repackage_tool, handle_repackage_result,
    SUBSCRIPTION_CHECK, MAIN_MENU, REPACKAGE_AUDIENCE, REPACKAGE_TOOL, REPACKAGE_RESULT
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('telegram_bot.log')
    ]
)
logger = logging.getLogger(__name__)

def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.error(f"============ ERROR OCCURRED ============")
    logger.error(f"Update: {update}")
    logger.error(f"Error: {context.error}")
    logger.error("========================================", exc_info=True)

_updater = None

def run_telegram_bot():
    """Start the bot."""
    global _updater
    try:
        # Initialize the bot
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            logger.error("Telegram bot token not found!")
            return

        # Clear any existing updater
        if _updater:
            logger.info("Stopping existing bot instance...")
            _updater.stop()
            _updater = None

        logger.info("Starting new bot instance...")

        # Create the Updater and pass it your bot's token
        _updater = Updater(token=TOKEN, use_context=True)
        dispatcher = _updater.dispatcher
        logger.info("Bot dispatcher initialized")

        # Add error handler
        dispatcher.add_error_handler(error_handler)
        logger.info("Error handler added")

        # Create conversation handler with states
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                SUBSCRIPTION_CHECK: [
                    CallbackQueryHandler(button_handler, pattern='^check_subscription$')
                ],
                MAIN_MENU: [
                    CallbackQueryHandler(handle_main_menu)
                ],
                REPACKAGE_AUDIENCE: [
                    MessageHandler(Filters.text & ~Filters.command, handle_repackage_audience),
                    CallbackQueryHandler(handle_main_menu, pattern='^back_to_menu$')
                ],
                REPACKAGE_TOOL: [
                    MessageHandler(Filters.text & ~Filters.command, handle_repackage_tool),
                    CallbackQueryHandler(handle_main_menu, pattern='^back_to_menu$')
                ],
                REPACKAGE_RESULT: [
                    MessageHandler(Filters.text & ~Filters.command, handle_repackage_result),
                    CallbackQueryHandler(handle_main_menu, pattern='^back_to_menu$')
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            allow_reentry=True
        )

        # Add handler to dispatcher
        dispatcher.add_handler(conv_handler)
        logger.info("Conversation handler added")

        # Start the Bot
        logger.info("Bot starting...")
        _updater.start_polling(drop_pending_updates=True)
        logger.info("Bot started successfully!")

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