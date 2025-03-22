from app import app
from main import run_telegram_bot
import threading
import logging
import os
import sys

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_bot_thread = None

def check_required_vars():
    """Check if all required environment variables are set."""
    required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SESSION_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

def start_bot():
    """Start the Telegram bot in a separate thread if not already running."""
    global _bot_thread
    if _bot_thread is None or not _bot_thread.is_alive():
        try:
            logger.info("Starting Telegram bot thread")
            _bot_thread = threading.Thread(target=run_telegram_bot)
            _bot_thread.daemon = True  # Make thread daemon so it exits when main thread exits
            _bot_thread.start()
            logger.info("Telegram bot thread started successfully")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot thread: {e}", exc_info=True)
            raise

def cleanup():
    """Cleanup function to be called on exit."""
    try:
        logger.info("Running cleanup...")
        if _bot_thread and _bot_thread.is_alive():
            logger.info("Stopping bot thread...")
            # Let the bot thread exit naturally as it's a daemon thread
        logger.info("Cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Only start the bot if running under Gunicorn
if os.environ.get('GUNICORN_CMD_ARGS'):
    if check_required_vars():
        try:
            start_bot()
            logger.info("Bot started successfully under Gunicorn")
        except Exception as e:
            logger.error(f"Failed to start bot under Gunicorn: {e}")
            sys.exit(1)
    else:
        logger.error("Cannot start server: missing required environment variables")
        sys.exit(1)