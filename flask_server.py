import os
import sys
import logging
from app import app

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('flask_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Check required environment variables
def check_required_vars():
    """Check if all required environment variables are set."""
    required_vars = ["SESSION_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

if __name__ == "__main__":
    try:
        # Check environment variables
        if not check_required_vars():
            logger.error("Required environment variables missing. Cannot start Flask application.")
            sys.exit(1)

        logger.info("Starting Flask web server...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Error starting Flask application: {e}", exc_info=True)
        sys.exit(1)