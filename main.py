import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Set up logging with more details
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def test_start(update, context):
    """Test start command handler"""
    logger.info("============ TEST COMMAND RECEIVED ============")
    logger.info(f"Update: {update}")
    logger.info(f"Message: {update.message}")
    logger.info(f"User: {update.effective_user}")
    logger.info(f"Chat ID: {update.effective_chat.id}")
    logger.info("=============================================")

    try:
        update.message.reply_text("Тестовая команда получена")
        logger.info("Reply sent successfully")
    except Exception as e:
        logger.error(f"Error sending reply: {e}", exc_info=True)

def log_all_updates(update, context):
    """Log all updates from Telegram"""
    logger.info("============ NEW UPDATE RECEIVED ============")
    logger.info(f"Update type: {update.effective_message.type if update.effective_message else 'Unknown'}")
    logger.info(f"Update ID: {update.update_id}")
    logger.info(f"Message: {update.message}")
    logger.info(f"User: {update.effective_user}")
    logger.info("===========================================")

    # Try to send a response to show the bot is working
    try:
        if update.message and update.message.text:
            update.message.reply_text(f"Получено сообщение: {update.message.text}")
            logger.info("Successfully sent reply to message")
    except Exception as e:
        logger.error(f"Error replying to message: {e}", exc_info=True)

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

        # Add a general update handler to log everything in group 1
        # This ensures it runs after command handlers but captures all updates
        dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command, log_all_updates), group=1)
        logger.info("Update logging handler added")

        # Add command handlers in group 0 (default)
        dispatcher.add_handler(CommandHandler('test', test_start))
        dispatcher.add_handler(CommandHandler('start', test_start))  # Using test_start for both commands
        logger.info("Command handlers added")

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
    main()