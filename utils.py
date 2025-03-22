import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def create_topic_examples_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with topic examples."""
    keyboard = [
        [InlineKeyboardButton("💼 Бизнес и предпринимательство", callback_data='topic_business')],
        [InlineKeyboardButton("🎯 Маркетинг и продажи", callback_data='topic_marketing')],
        [InlineKeyboardButton("💪 Личностный рост", callback_data='topic_growth')],
        [InlineKeyboardButton("🎨 Творчество и искусство", callback_data='topic_art')],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

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

def create_audience_examples_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with audience examples."""
    keyboard = [
        [InlineKeyboardButton("👔 Предприниматели", callback_data='audience_entrepreneurs')],
        [InlineKeyboardButton("💼 Фрилансеры", callback_data='audience_freelancers')],
        [InlineKeyboardButton("📱 Блогеры", callback_data='audience_bloggers')],
        [InlineKeyboardButton("👥 Начинающие специалисты", callback_data='audience_beginners')],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_monetization_examples_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with monetization examples."""
    keyboard = [
        [InlineKeyboardButton("📚 Инфопродукты", callback_data='monetization_info')],
        [InlineKeyboardButton("👨‍🏫 Консультации", callback_data='monetization_consult')],
        [InlineKeyboardButton("🎯 Реклама", callback_data='monetization_ads')],
        [InlineKeyboardButton("💰 Партнерские программы", callback_data='monetization_partner')],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_subscription_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with subscription button."""
    logger.info("Creating subscription keyboard...")
    keyboard = [[
        InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/expert_buyanov"),
        InlineKeyboardButton("✅ Я подписался", callback_data='check_subscription')
    ]]
    markup = InlineKeyboardMarkup(keyboard)
    logger.info("Created subscription keyboard")
    return markup

def create_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with only back to menu button."""
    logger.info("Creating back to menu keyboard...")
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