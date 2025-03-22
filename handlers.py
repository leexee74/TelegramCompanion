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
        logger.info("============ NEW START COMMAND RECEIVED ============")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Chat ID: {update.effective_chat.id}")
        logger.info("=================================================")

        # Clear any existing user data
        context.user_data.clear()
        logger.info("Cleared existing user data")

        # Check subscription status
        is_subscribed = check_subscription(context, user_id)
        logger.info(f"Subscription check result: {is_subscribed}")

        if not is_subscribed:
            keyboard = create_subscription_keyboard()
            logger.info("Sending subscription request message")
            update.message.reply_text(
                "👋 Для использования бота необходимо подписаться на канал @expert_buyanov",
                reply_markup=keyboard
            )
            return SUBSCRIPTION_CHECK

        # Show main menu with full description
        keyboard = create_main_menu_keyboard()
        logger.info("Creating main menu keyboard")

        menu_text = (
            "👋 Добро пожаловать в бот для создания контента!\n\n"
            "Выберите нужную опцию:\n\n"
            "📋 Контент-план / Посты - создание контент-плана\n"
            "🎯 Переупаковка продукта - создание продающего описания\n"
            "🔄 Начать заново - сброс настроек"
        )

        logger.info("Sending main menu message")
        update.message.reply_text(menu_text, reply_markup=keyboard)
        logger.info("Start command completed successfully")

        return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

def handle_main_menu(update: Update, context: CallbackContext) -> int:
    """Handle main menu button clicks."""
    try:
        query = update.callback_query
        query.answer()

        logger.info("============ MAIN MENU HANDLER ============")
        logger.info(f"Button pressed: {query.data}")
        logger.info("==========================================")

        if query.data == 'content_plan':
            # Reset conversation for content plan
            context.user_data.clear()
            query.message.edit_text(
                "⚡ Скоро будет добавлено!\n\n"
                "Возвращайтесь в главное меню:",
                reply_markup=create_main_menu_keyboard()
            )
            return MAIN_MENU

        elif query.data == 'repackage':
            # Reset conversation for repackaging
            context.user_data.clear()
            query.message.edit_text(
                "⚡ Скоро будет добавлено!\n\n"
                "Возвращайтесь в главное меню:",
                reply_markup=create_main_menu_keyboard()
            )
            return MAIN_MENU

        elif query.data == 'start_over':
            # Reset all user data
            context.user_data.clear()
            query.message.edit_text(
                "🔄 Настройки сброшены. Выберите действие:\n\n"
                "📋 Контент-план / Посты - создание контент-плана\n"
                "🎯 Переупаковка продукта - создание продающего описания\n"
                "🔄 Начать заново - сброс настроек",
                reply_markup=create_main_menu_keyboard()
            )
            return MAIN_MENU

        return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in main menu handler: {e}", exc_info=True)
        update.effective_message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
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
                query.message.edit_text(
                    menu_text,
                    reply_markup=create_main_menu_keyboard()
                )
                return MAIN_MENU
            else:
                query.message.edit_text(
                    "❌ Вы все еще не подписаны на канал @expert_buyanov\n"
                    "Подпишитесь и нажмите кнопку проверки ещё раз.",
                    reply_markup=create_subscription_keyboard()
                )
                return SUBSCRIPTION_CHECK

        # For all other buttons, use the main menu handler
        return handle_main_menu(update, context)

    except Exception as e:
        logger.error(f"Error in button handler: {e}", exc_info=True)
        update.effective_message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
        )
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    logger.info(f"User {update.effective_user.id} cancelled the conversation")
    update.message.reply_text('Операция отменена. Для начала напишите /start')
    return ConversationHandler.END