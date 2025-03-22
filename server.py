from app import app
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Start Flask app in development mode
    app.run(host='0.0.0.0', port=5000, debug=True)