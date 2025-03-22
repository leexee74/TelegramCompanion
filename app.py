from flask import Flask, render_template
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Configure database
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    logger.warning("DATABASE_URL not set; falling back to sqlite:///bot.db")
    database_url = "sqlite:///bot.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy with app
db.init_app(app)

# Basic route for health check
@app.route('/')
def home():
    return render_template('index.html')

# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created successfully")