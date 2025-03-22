import logging
import os
import sys
import threading
import time
import signal
from functools import partial
from main import run_telegram_bot
from app import app

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

# Global flag to track bot status
bot_is_running = False
bot_thread = None

def check_required_vars():
    """Check if all required environment variables are set."""
    required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SESSION_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

def signal_handler(signum, frame):
    """Handle termination signals gracefully."""
    logger.info(f"Received signal {signum}")
    cleanup()
    sys.exit(0)

def cleanup():
    """Clean up resources before shutdown."""
    global bot_is_running, bot_thread
    logger.info("Cleaning up resources...")
    bot_is_running = False
    if bot_thread and bot_thread.is_alive():
        logger.info("Waiting for bot thread to finish...")
        bot_thread.join(timeout=5)
    logger.info("Cleanup completed")

def start_bot_with_retry(max_retries=3, retry_delay=5):
    """Start Telegram bot with retry logic."""
    global bot_is_running, bot_thread

    if bot_is_running:
        logger.warning("Bot is already running")
        return False

    retries = 0
    while retries < max_retries:
        try:
            logger.info(f"Starting bot (attempt {retries + 1}/{max_retries})")
            bot_is_running = True
            run_telegram_bot()
            break
        except Exception as e:
            if "Conflict: terminated by other getUpdates request" in str(e):
                logger.warning(f"Bot conflict detected (attempt {retries + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retries += 1
                bot_is_running = False
            else:
                logger.error(f"Fatal bot error: {e}", exc_info=True)
                bot_is_running = False
                raise

    if retries >= max_retries:
        logger.error("Failed to start bot after maximum retries")
        bot_is_running = False
        return False

    return True

def run_flask_app():
    """Run Flask application with proper error handling."""
    try:
        logger.info("Starting Flask application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Error running Flask app: {e}", exc_info=True)
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Set up signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        # Check environment variables
        if not check_required_vars():
            logger.error("Required environment variables missing. Cannot start application.")
            sys.exit(1)

        logger.info("Starting application components...")

        # Start Telegram bot in a separate thread with retry logic
        bot_thread = threading.Thread(target=start_bot_with_retry)
        bot_thread.daemon = True
        bot_thread.start()
        logger.info("Telegram bot thread started")

        # Start Flask app in the main thread
        run_flask_app()

    except Exception as e:
        logger.error(f"Error starting application: {e}", exc_info=True)
        cleanup()
        sys.exit(1)