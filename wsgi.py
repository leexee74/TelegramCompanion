from flask import Flask
import threading
import logging
import os
import sys
from app import app  # Import the Flask app

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('wsgi.log')
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

def start_telegram_bot():
    """Start the Telegram bot in a separate thread."""
    try:
        logger.info("Starting Telegram bot thread...")
        from main import run_telegram_bot
        run_telegram_bot()
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}", exc_info=True)
        raise

# Initialize application
try:
    logger.info("Starting WSGI application initialization...")

    # Check environment variables before starting
    if not check_required_vars():
        logger.error("Required environment variables missing. Cannot start application.")
        sys.exit(1)

    # Start Telegram bot in a separate thread
    bot_thread = threading.Thread(target=start_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("Telegram bot thread started successfully")

    # Export the Flask app for Gunicorn
    logger.info("WSGI application initialization completed")
except Exception as e:
    logger.error(f"Failed to initialize WSGI application: {e}", exc_info=True)
    raise

# This is the application variable that Gunicorn expects
application = app