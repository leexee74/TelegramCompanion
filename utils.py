import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create the main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("📋 Контент-план / Посты", callback_data='content_plan')],
        [InlineKeyboardButton("🎯 Переупаковка продукта", callback_data='repackage')],
        [InlineKeyboardButton("🔄 Начать заново", callback_data='start_over')]
    ]
    return InlineKeyboardMarkup(keyboard)

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

def create_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with back to menu button."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 Вернуться в меню", callback_data='back_to_menu')
    ]])

def check_subscription(context: CallbackContext, user_id: int) -> bool:
    """Check if user is subscribed to the required channel."""
    try:
        # Проверка статуса участника
        member = context.bot.get_chat_member(chat_id="@expert_buyanov", user_id=user_id)

        # Логируем полученные данные
        logger.info("=============== SUBSCRIPTION CHECK ===============")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Member status: {member.status}")
        logger.info("===============================================")

        # Проверяем только основные статусы
        is_member = member.status in ['member', 'administrator', 'creator']

        # Возвращаем результат проверки
        return is_member

    except Exception as e:
        logger.error(f"Subscription check error for user {user_id}: {e}")
        # В случае ошибки считаем, что пользователь не подписан
        return False