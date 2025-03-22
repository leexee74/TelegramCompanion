from app import app
import logging
import os
import sys
import threading
import time
from main import run_telegram_bot

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log')
    ]
)
logger = logging.getLogger(__name__)

def check_required_vars():
    """Check if all required environment variables are set."""
    required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SESSION_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

def start_bot_with_retry(max_retries=3, retry_delay=5):
    """Start Telegram bot with retry logic."""
    retries = 0
    while retries < max_retries:
        try:
            run_telegram_bot()
            break
        except Exception as e:
            if "Conflict: terminated by other getUpdates request" in str(e):
                logger.warning(f"Bot conflict detected (attempt {retries + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retries += 1
            else:
                logger.error(f"Fatal bot error: {e}", exc_info=True)
                raise

    if retries >= max_retries:
        logger.error("Failed to start bot after maximum retries")
        return False
    return True

if __name__ == "__main__":
    try:
        # Check environment variables
        if not check_required_vars():
            logger.error("Required environment variables missing. Cannot start application.")
            sys.exit(1)

        logger.info("Starting application components...")

        # Start Telegram bot in a separate thread with retry logic
        bot_thread = threading.Thread(target=start_bot_with_retry)
        bot_thread.daemon = True
        bot_thread.start()
        logger.info("Telegram bot thread started successfully")

        # Start Flask app
        logger.info("Starting Flask application...")
        app.run(host='0.0.0.0', port=5000, debug=True)

    except Exception as e:
        logger.error(f"Error starting application: {e}", exc_info=True)
        sys.exit(1)