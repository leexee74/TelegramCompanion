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
        [InlineKeyboardButton("🎓 Консультации, курсы", callback_data='consulting')],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_style_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for writing style options."""
    keyboard = [
        [InlineKeyboardButton("⚡ Агрессивный", callback_data='aggressive')],
        [InlineKeyboardButton("📊 Деловой", callback_data='business')],
        [InlineKeyboardButton("🤣 Юмористический", callback_data='humorous')],
        [InlineKeyboardButton("✍ Свой стиль", callback_data='custom')],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_subscription_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with subscription button."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/expert_buyanov"),
        InlineKeyboardButton("✅ Я подписался", callback_data='check_subscription')
    ]])

def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard."""
    logger.info("Creating main menu keyboard...")
    keyboard = [
        [InlineKeyboardButton("📋 Контент-план / Посты", callback_data='content_plan')],
        [InlineKeyboardButton("🎯 Переупаковка продукта", callback_data='repackage')],
        [InlineKeyboardButton("🔄 Начать заново", callback_data='start_over')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    logger.info(f"Created main menu keyboard with buttons: {[btn.text for row in keyboard for btn in row]}")
    return markup

def create_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with only back to menu button."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 Вернуться в меню", callback_data='back_to_menu')
    ]])

def check_subscription(context: CallbackContext, user_id: int) -> bool:
    """Check if user is subscribed to the required channel."""
    try:
        member = context.bot.get_chat_member(chat_id="@expert_buyanov", user_id=user_id)
        logger.info(f"Subscription check for user {user_id}: {member.status}")
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Subscription check error for user {user_id}: {e}")
        return False