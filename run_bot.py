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
        # Check if required environment variables are set
        required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SESSION_SECRET"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            sys.exit(1)

        logger.info("Starting Telegram bot...")
        run_telegram_bot()
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}", exc_info=True)
        sys.exit(1)