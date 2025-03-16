import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

def create_monetization_keyboard() -> List[List[InlineKeyboardButton]]:
    """Create keyboard for monetization options."""
    return [
        [InlineKeyboardButton("📢 Реклама", callback_data='advertising')],
        [InlineKeyboardButton("🛍️ Продажа товаров", callback_data='products')],
        [InlineKeyboardButton("🔧 Продажа услуг", callback_data='services')],
        [InlineKeyboardButton("🎓 Консультации, курсы", callback_data='consulting')]
    ]

def create_style_keyboard() -> List[List[InlineKeyboardButton]]:
    """Create keyboard for writing style options."""
    return [
        [InlineKeyboardButton("⚡ Агрессивный", callback_data='aggressive')],
        [InlineKeyboardButton("📊 Деловой", callback_data='business')],
        [InlineKeyboardButton("🤣 Юмористический", callback_data='humorous')],
        [InlineKeyboardButton("✍ Свой стиль", callback_data='custom')]
    ]

def format_post(post: str) -> str:
    """Format the post text with proper Telegram markdown."""
    # Replace common markdown characters
    post = post.replace('*', '\\*')
    post = post.replace('_', '\\_')
    post = post.replace('`', '\\`')
    post = post.replace('[', '\\[')
    
    return post
