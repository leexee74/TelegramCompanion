import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import CallbackContext
from typing import List

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )

def create_monetization_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for monetization options."""
    keyboard = [
        [InlineKeyboardButton("📢 Реклама", callback_data='advertising')],
        [InlineKeyboardButton("🛍️ Продажа товаров", callback_data='products')],
        [InlineKeyboardButton("🔧 Продажа услуг", callback_data='services')],
        [InlineKeyboardButton("🎓 Консультации, курсы", callback_data='consulting')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_style_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for writing style options."""
    keyboard = [
        [InlineKeyboardButton("⚡ Агрессивный", callback_data='aggressive')],
        [InlineKeyboardButton("📊 Деловой", callback_data='business')],
        [InlineKeyboardButton("🤣 Юмористический", callback_data='humorous')],
        [InlineKeyboardButton("✍ Свой стиль", callback_data='custom')]
    ]
    return InlineKeyboardMarkup(keyboard)

def format_post(post: str) -> str:
    """Format the post text with proper Telegram markdown."""
    # Replace common markdown characters
    post = post.replace('*', '\\_')
    post = post.replace('`', '\\`')
    post = post.replace('[', '\\[')
    return post

def create_subscription_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with subscription button."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/expert_buyanov"),
        InlineKeyboardButton("✅ Я подписался", callback_data='check_subscription')
    ]])

def check_subscription(context: CallbackContext, user_id: int) -> bool:
    """Check if user is subscribed to the required channel."""
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"Checking subscription for user {user_id}")

        member = context.bot.get_chat_member(chat_id="@expert_buyanov", user_id=user_id)
        logger.info(f"User {user_id} subscription status: {member.status}")

        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error checking subscription for user {user_id}: {e}", exc_info=True)
        return False