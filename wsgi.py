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
    """Start the Telegram bot in a daemon thread."""
    global _bot_thread
    try:
        _bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        _bot_thread.start()
        logger.info("Telegram bot thread started successfully")
    except Exception as e:
        logger.error(f"Failed to start bot thread: {e}")
        raise

# Initialize bot when running under Gunicorn
if os.environ.get('GUNICORN_CMD_ARGS'):
    if check_required_vars():
        try:
            start_bot()
            logger.info("Bot initialization completed")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            sys.exit(1)