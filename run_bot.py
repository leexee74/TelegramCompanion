import logging
import os
import sys
from main import run_telegram_bot

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('telegram_bot.log')
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting Telegram bot...")
        run_telegram_bot()
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}", exc_info=True)
        sys.exit(1)
