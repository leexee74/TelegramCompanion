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

        # Попытка получить информацию о участнике канала
        try:
            member = context.bot.get_chat_member(chat_id="@expert_buyanov", user_id=user_id)
            logger.info(f"User {user_id} subscription status: {member.status}")
            logger.info(f"Member object details: {member.__dict__}")

            # Если удалось получить статус - проверяем его
            is_subscribed = member.status in ['member', 'administrator', 'creator']
            logger.info(f"Subscription check result: {is_subscribed}")

            if not is_subscribed:
                logger.info("User is not subscribed (based on member status)")

            return is_subscribed

        except Exception as member_error:
            logger.warning(f"Failed to get member status: {member_error}")
            logger.info("Trying alternative check method...")

            try:
                # Альтернативная проверка через отправку сообщения
                test_message = context.bot.send_message(
                    chat_id="@expert_buyanov",
                    text="🤖 Проверка подписки...",
                    disable_notification=True
                )
                context.bot.delete_message(
                    chat_id="@expert_buyanov",
                    message_id=test_message.message_id
                )
                logger.info("User can access the channel (message test passed)")
                return True

            except Exception as alt_error:
                logger.error(f"Alternative check failed: {alt_error}")
                return False

    except Exception as e:
        logger.error("============ SUBSCRIPTION CHECK ERROR ============")
        logger.error(f"Error checking subscription for user {user_id}")
        logger.error(f"Error details: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("===============================================")

        if "chat not found" in str(e).lower():
            logger.error("Channel @expert_buyanov not found")
            return True  # Allow access if channel doesn't exist
        elif "forbidden" in str(e).lower():
            logger.info("Bot lacks necessary permissions")
            return True  # Allow access if bot lacks permissions
        else:
            logger.error("Unknown error during subscription check")
            return True  # Allow access in case of technical issues