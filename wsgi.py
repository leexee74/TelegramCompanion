import logging
import os
import sys
import threading
import time
from main import run_telegram_bot
from app import app

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

def start_bot():
    """Start Telegram bot in a separate thread."""
    global bot_is_running, bot_thread

    if bot_is_running:
        logger.warning("Bot is already running")
        return

    try:
        logger.info("Starting Telegram bot...")
        bot_is_running = True
        run_telegram_bot()
        logger.info("Telegram bot started successfully")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}", exc_info=True)
        bot_is_running = False
        raise

# Check required environment variables
if not check_required_vars():
    logger.error("Required environment variables missing. Cannot start application.")
    sys.exit(1)

logger.info("All required environment variables are present")

# Start Telegram bot in a separate thread when running with gunicorn
if os.environ.get('SERVER_SOFTWARE', '').startswith('gunicorn'):
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("Started Telegram bot thread in gunicorn environment")

# This is the application variable that Gunicorn expects
application = app
# Also expose as 'app' for compatibility
app = application

logger.info("WSGI application initialized successfully")