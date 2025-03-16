from app import app
from main import run_telegram_bot
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("WSGI module loaded - initializing Flask app and Telegram bot")

# Start Telegram bot in a separate thread when running in production
if __name__ != "__main__":  # This ensures bot only starts when running via gunicorn
    try:
        logger.info("Starting Telegram bot thread")
        bot_thread = threading.Thread(target=run_telegram_bot)
        bot_thread.daemon = True  # Thread will be terminated when main process exits
        bot_thread.start()
        logger.info("Telegram bot thread started successfully")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot thread: {e}", exc_info=True)

# Run Flask app directly if running this file
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)