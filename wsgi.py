from app import app
from main import run_telegram_bot, stop_telegram_bot
import threading
import logging
import os
import atexit
import signal

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
        stop_telegram_bot()
        logger.info("Cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Register cleanup function
atexit.register(cleanup)

# Register signal handlers
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}")
    cleanup()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Handle Flask application
if __name__ == "__main__":
    # Running directly
    if check_required_vars():
        app.run(host="0.0.0.0", port=5000)
else:
    # Running under Gunicorn
    if check_required_vars():
        try:
            start_bot()
            logger.info("Bot started successfully under Gunicorn")
        except Exception as e:
            logger.error(f"Failed to start bot under Gunicorn: {e}")