from flask import Flask, render_template
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Starting Flask application initialization...")

# Initialize Flask app
app = Flask(__name__)

# Set up secret key with proper error handling
try:
    app.secret_key = os.environ.get("SESSION_SECRET")
    if not app.secret_key:
        logger.error("SESSION_SECRET environment variable not set!")
        raise RuntimeError("SESSION_SECRET environment variable must be set")
    logger.info("Secret key configured successfully")
except Exception as e:
    logger.error(f"Failed to configure secret key: {e}", exc_info=True)
    raise

# Configure database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Configure database with proper error handling
try:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.warning("DATABASE_URL not set; falling back to sqlite:///bot.db")
        database_url = "sqlite:///bot.db"

    logger.info(f"Using database: {database_url.split('@')[0].split(':')[0]}://***:***@***")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Initialize SQLAlchemy with app
    db.init_app(app)
    logger.info("SQLAlchemy initialized successfully")
except Exception as e:
    logger.error(f"Failed to configure database: {e}", exc_info=True)
    raise

# Basic route for health check
@app.route('/')
def home():
    logger.info("Serving index page")
    return render_template('index.html')

# Create database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}", exc_info=True)
        raise

logger.info("Flask application initialization completed successfully")

if __name__ == "__main__":
    # Running directly
    app.run(host='0.0.0.0', port=5000, debug=True)