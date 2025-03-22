from app import app
import logging
import os

logger = logging.getLogger(__name__)

def check_required_vars():
    """Check if all required environment variables are set."""
    required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SESSION_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

if __name__ == "__main__":
    if check_required_vars():
        # Start Flask app in development mode with reloader disabled
        # to prevent duplicate bot instances
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    else:
        logger.error("Cannot start server: missing required environment variables")