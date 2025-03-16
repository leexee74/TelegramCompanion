
from app import app
from main import run_telegram_bot
import threading
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_required_vars():
    required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SESSION_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

# Start Telegram bot in a separate thread when running in production
if __name__ != "__main__" and check_required_vars():  
    try:
        logger.info("Starting Telegram bot thread")
        bot_thread = threading.Thread(target=run_telegram_bot)
        bot_thread.daemon = True
        bot_thread.start()
        logger.info("Telegram bot thread started successfully")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot thread: {e}", exc_info=True)

if __name__ == "__main__":
    if check_required_vars():
        app.run(host="0.0.0.0", port=5000)
