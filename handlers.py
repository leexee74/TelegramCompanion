import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from utils import create_main_menu_keyboard, create_subscription_keyboard, check_subscription

logger = logging.getLogger(__name__)

# Conversation states
(SUBSCRIPTION_CHECK, MAIN_MENU) = range(2)

def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and check subscription."""
    try:
        user_id = update.effective_user.id
        logger.info("============ NEW START HANDLER INVOKED ============")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Chat ID: {update.effective_chat.id}")
        logger.info("=======================================")

        # Clear any existing user data
        context.user_data.clear()
        logger.info("Cleared existing user data")

        # Check subscription status
        is_subscribed = check_subscription(context, user_id)
        logger.info(f"Subscription check result for user {user_id}: {is_subscribed}")

        if not is_subscribed:
            keyboard = create_subscription_keyboard()
            logger.info("Created subscription keyboard")
            update.message.reply_text(
                "👋 Для использования бота необходимо подписаться на канал @expert_buyanov",
                reply_markup=keyboard
            )
            return SUBSCRIPTION_CHECK

        # Show main menu with full description
        keyboard = create_main_menu_keyboard()
        logger.info(f"Created main menu keyboard with buttons: {[btn.text for row in keyboard.inline_keyboard for btn in row]}")

        menu_text = (
            "👋 Добро пожаловать в бот для создания контента!\n\n"
            "Выберите нужную опцию:\n\n"
            "📋 Контент-план / Посты - создание контент-плана\n"
            "🎯 Переупаковка продукта - создание продающего описания\n"
            "🔄 Начать заново - сброс настроек"
        )

        logger.info("Sending menu message with text:")
        logger.info(menu_text)

        update.message.reply_text(menu_text, reply_markup=keyboard)
        logger.info("Successfully sent main menu message")

        return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

def button_handler(update: Update, context: CallbackContext) -> int:
    """Handle button callbacks."""
    try:
        query = update.callback_query
        query.answer()

        logger.info("============ BUTTON HANDLER ============")
        logger.info(f"Button data: {query.data}")
        logger.info("======================================")

        # Handle subscription check
        if query.data == 'check_subscription':
            is_subscribed = check_subscription(context, update.effective_user.id)
            if is_subscribed:
                menu_text = (
                    "👋 Добро пожаловать в бот для создания контента!\n\n"
                    "Выберите нужную опцию:\n\n"
                    "📋 Контент-план / Посты - создание контент-плана\n"
                    "🎯 Переупаковка продукта - создание продающего описания\n"
                    "🔄 Начать заново - сброс настроек"
                )
                query.message.reply_text(
                    menu_text,
                    reply_markup=create_main_menu_keyboard()
                )
                return MAIN_MENU
            else:
                query.message.reply_text(
                    "❌ Вы все еще не подписаны на канал @expert_buyanov\n"
                    "Подпишитесь и нажмите кнопку проверки ещё раз.",
                    reply_markup=create_subscription_keyboard()
                )
                return SUBSCRIPTION_CHECK

        return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in button handler: {e}", exc_info=True)
        update.effective_message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
        )
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    update.message.reply_text('Операция отменена. Для начала напишите /start')
    return ConversationHandler.END