from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import DateTime, func

class UserData(db.Model):
    __tablename__ = 'user_data'
    __table_args__ = {'extend_existing': True}

    chat_id = db.Column(db.BigInteger, primary_key=True)
    tone_of_voice = db.Column(db.String(255))
    audience = db.Column(db.String(255))
    content_theme = db.Column(db.String(255))
    joined_at = db.Column(DateTime, default=func.now())

class ScheduledMessage(db.Model):
    __tablename__ = 'scheduled_messages'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    step_order = db.Column(db.Integer, nullable=False)
    message_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(255))
    delay_minutes = db.Column(db.Integer, default=0)
    created_at = db.Column(DateTime, default=func.now())

class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    __table_args__ = {'extend_existing': True}

    chat_id = db.Column(db.BigInteger, primary_key=True)
    joined_at = db.Column(DateTime, default=func.now())

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))