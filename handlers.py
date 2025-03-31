import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from utils import create_main_menu_keyboard, create_subscription_keyboard, check_subscription, create_back_to_menu_keyboard
from prompts import generate_product_repackaging, generate_content_plan
from database import save_user_data, get_user_data

logger = logging.getLogger(__name__)

# Conversation states
(SUBSCRIPTION_CHECK, MAIN_MENU, 
 REPACKAGE_AUDIENCE, REPACKAGE_TOOL, REPACKAGE_RESULT,
 CONTENT_TOPIC, CONTENT_AUDIENCE, CONTENT_MONETIZATION,
 CONTENT_PRODUCT) = range(9)

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

        # Без проверки подписки - сразу показываем главное меню
        # Проверка подписки будет происходить после генерации контент-плана

        # Show main menu with full description
        keyboard = create_main_menu_keyboard()
        logger.info("Creating main menu keyboard")

        menu_text = (
            "👋 Добро пожаловать! Я помогу вам создать эффективный контент-план для вашего Telegram канала.\n\n"
            "✅ Создам последовательный план из 14 постов\n"
            "✅ Посты будут постепенно прогревать вашу аудиторию к покупке\n"
            "✅ В финале - мощное предложение для продажи ваших товаров/услуг/курсов\n\n"
            "Выберите нужную опцию:\n\n"
            "📋 Контент-план / Посты - создание плана с постами для прогрева к продажам\n"
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
        logger.info(f"User ID: {update.effective_user.id}")
        logger.info(f"Button pressed: {query.data}")
        logger.info("==========================================")

        if query.data == 'content_plan':
            # Start content plan flow
            context.user_data.clear()
            logger.info("Starting content plan flow")
            query.message.edit_text(
                "📋 Для составления контент-плана мне нужно задать несколько вопросов.\n\n"
                "Первый вопрос: какая тематика вашего канала?\n\n"
                "Например:\n"
                "- Развитие бизнеса и предпринимательство\n"
                "- Маркетинг и продажи в социальных сетях\n"
                "- Личностный рост и саморазвитие\n"
                "- Творчество и креативные проекты",
                reply_markup=create_back_to_menu_keyboard()
            )
            return CONTENT_TOPIC

        elif query.data == 'repackage':
            # Start repackaging flow
            context.user_data.clear()
            query.message.edit_text(
                "🎯 Давайте переупакуем ваш продукт!\n\n"
                "Для начала, скажите:\n"
                "Кто ваша целевая аудитория?",
                reply_markup=create_back_to_menu_keyboard()
            )
            return REPACKAGE_AUDIENCE

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

        elif query.data == 'back_to_menu':
            context.user_data.clear()
            query.message.edit_text(
                "👋 Добро пожаловать! Я помогу вам создать эффективный контент-план для вашего Telegram канала.\n\n"
                "✅ Создам последовательный план из 14 постов\n"
                "✅ Посты будут постепенно прогревать вашу аудиторию к покупке\n"
                "✅ В финале - мощное предложение для продажи ваших товаров/услуг/курсов\n\n"
                "Выберите нужную опцию:\n\n"
                "📋 Контент-план / Посты - создание плана с постами для прогрева к продажам\n"
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

def handle_content_topic(update: Update, context: CallbackContext) -> int:
    """Handle topic input for content plan."""
    try:
        if update.callback_query:
            if update.callback_query.data == 'back_to_menu':
                return handle_main_menu(update, context)

        # Log incoming message
        logger.info(f"============ CONTENT TOPIC HANDLER ============")
        logger.info(f"User ID: {update.effective_user.id}")
        logger.info(f"Message text: {update.message.text}")
        logger.info("=============================================")

        # Save topic info
        context.user_data['topic'] = update.message.text
        logger.info(f"Saved topic info: {update.message.text}")

        # Ask for audience info
        update.message.reply_text(
            "👥 Отлично! Теперь опишите вашу целевую аудиторию.\n\n"
            "Например:\n"
            "- Предприниматели, владельцы малого и среднего бизнеса\n"
            "- Фрилансеры и удаленные специалисты\n"
            "- Блогеры и контент-мейкеры\n"
            "- Начинающие специалисты, желающие развиваться",
            reply_markup=create_back_to_menu_keyboard()
        )
        return CONTENT_AUDIENCE

    except Exception as e:
        logger.error(f"Error in content topic handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, вернитесь в главное меню.",
            reply_markup=create_main_menu_keyboard()
        )
        return MAIN_MENU

def handle_content_audience(update: Update, context: CallbackContext) -> int:
    """Handle audience input for content plan."""
    try:
        if update.callback_query:
            if update.callback_query.data == 'back_to_menu':
                return handle_main_menu(update, context)

        # Log incoming message
        logger.info(f"============ CONTENT AUDIENCE HANDLER ============")
        logger.info(f"User ID: {update.effective_user.id}")
        logger.info(f"Message text: {update.message.text}")
        logger.info("===============================================")

        # Save audience info
        context.user_data['audience'] = update.message.text
        logger.info(f"Saved audience info: {update.message.text}")

        # Ask for monetization info
        update.message.reply_text(
            "💰 Как планируете монетизировать канал?\n\n"
            "Например:\n"
            "- Продажа онлайн-курсов и инфопродуктов\n"
            "- Индивидуальные консультации и коучинг\n"
            "- Реклама и спонсорские интеграции\n"
            "- Партнерские программы и комиссионные",
            reply_markup=create_back_to_menu_keyboard()
        )
        return CONTENT_MONETIZATION

    except Exception as e:
        logger.error(f"Error in content audience handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, вернитесь в главное меню.",
            reply_markup=create_main_menu_keyboard()
        )
        return MAIN_MENU

def handle_content_monetization(update: Update, context: CallbackContext) -> int:
    """Handle monetization input for content plan."""
    try:
        if update.callback_query:
            if update.callback_query.data == 'back_to_menu':
                return handle_main_menu(update, context)

        # Log incoming message
        logger.info(f"============ CONTENT MONETIZATION HANDLER ============")
        logger.info(f"User ID: {update.effective_user.id}")
        logger.info(f"Message text: {update.message.text}")
        logger.info("=================================================")

        # Save monetization info
        context.user_data['monetization'] = update.message.text
        logger.info(f"Saved monetization info: {update.message.text}")

        # Ask for product details
        update.message.reply_text(
            "📦 Опишите подробнее ваш продукт/услугу/курс, который планируете продавать:",
            reply_markup=create_back_to_menu_keyboard()
        )
        return CONTENT_PRODUCT

    except Exception as e:
        logger.error(f"Error in content monetization handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, вернитесь в главное меню.",
            reply_markup=create_main_menu_keyboard()
        )
        return MAIN_MENU

def handle_content_product(update: Update, context: CallbackContext) -> int:
    """Handle product details input for content plan."""
    try:
        # Log incoming message
        logger.info(f"============ CONTENT PRODUCT HANDLER ============")
        logger.info(f"User ID: {update.effective_user.id}")
        logger.info(f"Message text: {update.message.text}")
        logger.info("=============================================")

        # Save product details
        context.user_data['product_details'] = update.message.text
        logger.info(f"Saved product details: {update.message.text}")

        # Generate content plan
        update.message.reply_text("🔄 Генерирую контент-план...")

        # Log before generating content plan
        logger.info("Generating content plan with data:")
        logger.info(context.user_data)

        content_plan = generate_content_plan(context.user_data)

        # Log after generating content plan
        logger.info("Content plan generated successfully")

        # Save content plan to database
        user_id = update.effective_user.id
        save_user_data(user_id, context.user_data)
        logger.info(f"Saved user data to database for user {user_id}")

        # Сохраняем контент-план в user_data
        context.user_data['content_plan'] = content_plan

        # Отправляем контент-план и проверяем подписку
        update.message.reply_text(
            f"{content_plan}\n\n"
            "✅ Твой персональный контент-план уже готов!\n\n"
            "Остался последний шаг, чтобы получить посты к этому контент-плану и создавать новые планы без ограничений.\n\n"
            "👉 Просто подпишись на автора бота — Александра Буянова @expert_buyanov.\n"
            "Это займёт всего 3 секунды, а взамен ты получишь не только доступ ко всем моим функциям, но и сможешь следить за тем, "
            "как Александр в реальном времени монетизирует Telegram-канал с нуля.\n\n"
            "🔥 Почему стоит подписаться:\n"
            "— Получай готовые посты в один клик.\n"
            "— Генерируй новые контент-планы под любые темы и задачи.\n"
            "— Учись зарабатывать в Telegram на живом примере Александра.\n\n"
            "Жду твоей подписки, чтобы продолжить! 🚀",
            reply_markup=create_subscription_keyboard()
        )
        return SUBSCRIPTION_CHECK

    except Exception as e:
        logger.error(f"Error in content product handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка при генерации контент-плана.\n"
            "Пожалуйста, вернитесь в главное меню и попробуйте снова.",
            reply_markup=create_main_menu_keyboard()
        )
        return MAIN_MENU

def handle_repackage_audience(update: Update, context: CallbackContext) -> int:
    """Handle audience input for product repackaging."""
    try:
        # Save audience info
        context.user_data['audience'] = update.message.text
        logger.info(f"Saved audience info: {update.message.text}")

        # Ask for tool info
        update.message.reply_text(
            "👍 Отлично! Теперь скажите:\n"
            "Какой инструмент или продукт вы предлагаете?",
            reply_markup=create_back_to_menu_keyboard()
        )
        return REPACKAGE_TOOL

    except Exception as e:
        logger.error(f"Error in repackage audience handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, вернитесь в главное меню.",
            reply_markup=create_main_menu_keyboard()
        )
        return MAIN_MENU

def handle_repackage_tool(update: Update, context: CallbackContext) -> int:
    """Handle tool info for product repackaging."""
    try:
        # Save tool info
        context.user_data['tool'] = update.message.text
        logger.info(f"Saved tool info: {update.message.text}")

        # Ask for result info
        update.message.reply_text(
            "💫 Прекрасно! И последний вопрос:\n"
            "Какой результат получит ваша аудитория?",
            reply_markup=create_back_to_menu_keyboard()
        )
        return REPACKAGE_RESULT

    except Exception as e:
        logger.error(f"Error in repackage tool handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, вернитесь в главное меню.",
            reply_markup=create_main_menu_keyboard()
        )
        return MAIN_MENU

def handle_repackage_result(update: Update, context: CallbackContext) -> int:
    """Handle result info and generate repackaged content."""
    try:
        # Save result info
        context.user_data['result'] = update.message.text
        logger.info(f"Saved result info: {update.message.text}")

        # Generate repackaged content
        update.message.reply_text("🔄 Генерирую переупаковку продукта...")
        repackaged_content = generate_product_repackaging(context.user_data)

        # Send the result and return to main menu
        update.message.reply_text(
            f"{repackaged_content}\n\n"
            "Выберите следующее действие:",
            reply_markup=create_main_menu_keyboard()
        )
        return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in repackage result handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка при генерации контента.\n"
            "Пожалуйста, вернитесь в главное меню и попробуйте снова.",
            reply_markup=create_main_menu_keyboard()
        )
        return MAIN_MENU

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
                # Если есть контент-план в user_data, значит проверка происходит после его генерации
                if 'content_plan' in context.user_data:
                    query.message.edit_text(
                        "Поздравляем, все функции бота теперь активированы. "
                        "Введи номер поста из контент плана, который хочешь сгенерировать."
                    )
                    # Здесь должна быть обработка ввода номера поста, но это отдельная функция
                    # Возвращаемся в главное меню пока что
                    return MAIN_MENU
                else:
                    # Обычная проверка подписки при старте бота (старое поведение)
                    menu_text = (
                        "👋 Добро пожаловать! Я помогу вам создать эффективный контент-план для вашего Telegram канала.\n\n"
                        "✅ Создам последовательный план из 14 постов\n"
                        "✅ Посты будут постепенно прогревать вашу аудиторию к покупке\n"
                        "✅ В финале - мощное предложение для продажи ваших товаров/услуг/курсов\n\n"
                        "Выберите нужную опцию:\n\n"
                        "📋 Контент-план / Посты - создание плана с постами для прогрева к продажам\n"
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