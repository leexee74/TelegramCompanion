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

# Set up logging with more details
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def debug_start(update, context):
    """Debug start command handler"""
    logger.info("Debug start command received")
    logger.info(f"Update: {update}")
    logger.info(f"Message: {update.message}")
    logger.info(f"User: {update.effective_user}")
    update.message.reply_text("Debug start command received. Check logs for details.")

def test_start(update, context):
    """Test start command handler"""
    logger.info("Test start command received")
    update.message.reply_text("Test start command received")

def message_handler(update, context):
    """Log all incoming messages"""
    logger.info("============ NEW MESSAGE ============")
    logger.info(f"Received message: {update.message.text if update.message else 'No message'}")
    logger.info(f"Update type: {update.effective_message.type if update.effective_message else 'Unknown'}")
    logger.info(f"From user: {update.effective_user}")
    logger.info(f"Chat type: {update.message.chat.type if update.message else 'Unknown'}")
    logger.info("====================================")

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

        # Add message handler to log all incoming messages FIRST
        message_logging_handler = MessageHandler(
            Filters.all & ~Filters.command,
            message_handler
        )
        dispatcher.add_handler(message_logging_handler, group=1)
        logger.info("Message handler added")

        # Add debug command handlers
        dispatcher.add_handler(CommandHandler('debug_start', debug_start))
        dispatcher.add_handler(CommandHandler('test', test_start))
        dispatcher.add_handler(CommandHandler('start', debug_start))
        logger.info("Command handlers added")

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