import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

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

def create_subscription_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with subscription button."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/expert_buyanov"),
        InlineKeyboardButton("✅ Я подписался", callback_data='check_subscription')
    ]])

def check_subscription(context: CallbackContext, user_id: int) -> bool:
    """Check if user is subscribed to the required channel."""
    try:
        logger.info(f"============ CHECKING SUBSCRIPTION ============")
        logger.info(f"Checking subscription for user {user_id}")
        member = context.bot.get_chat_member(chat_id="@expert_buyanov", user_id=user_id)
        logger.info(f"User {user_id} subscription status: {member.status}")
        logger.info(f"Member object details: {member}")
        logger.info("============================================")

        is_subscribed = member.status in ['member', 'administrator', 'creator']
        logger.info(f"Subscription check result: {is_subscribed}")
        return is_subscribed
    except Exception as e:
        logger.error(f"Error checking subscription for user {user_id}: {e}", exc_info=True)
        return False