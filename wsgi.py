import logging
import os
import sys

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

# Import Flask app first
try:
    from app import app
    logger.info("Successfully imported Flask app")
except Exception as e:
    logger.error(f"Failed to import Flask app: {e}", exc_info=True)
    raise

# Check required environment variables
def check_required_vars():
    """Check if all required environment variables are set."""
    required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SESSION_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

if not check_required_vars():
    logger.error("Required environment variables missing. Cannot start application.")
    sys.exit(1)

logger.info("All required environment variables are present")

# This is the application variable that Gunicorn expects
application = app
# Also expose as 'app' for compatibility
app = application
logger.info("WSGI application initialized successfully")