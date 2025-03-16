import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import save_user_data, get_user_data
from prompts import generate_content_plan, generate_post
from utils import create_monetization_keyboard, create_style_keyboard

logger = logging.getLogger(__name__)

# Conversation states
TOPIC, AUDIENCE, MONETIZATION, PRODUCT_DETAILS, PREFERENCES, STYLE, EMOTIONS, EXAMPLES = range(8)

def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask for channel topic."""
    keyboard = [[InlineKeyboardButton("Начать работу", callback_data='start_work')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Добро пожаловать! Я помогу вам создать engaging посты для вашего Telegram канала.",
        reply_markup=reply_markup
    )
    return TOPIC

def process_examples(update: Update, context: CallbackContext) -> int:
    """Process collected examples and generate content plan."""
    try:
        logger.info("Processing examples with data: %s", context.user_data)

        # Combine all examples into one string
        examples_text = "\n---\n".join(context.user_data.get('examples', []))
        context.user_data['examples'] = examples_text

        # Show processing message
        message = update.callback_query.message if update.callback_query else update.message
        message.reply_text("🔄 Генерирую контент-план на 14 дней...")

        # Generate and save content plan
        logger.info("Generating content plan...")
        content_plan = generate_content_plan(context.user_data)
        context.user_data['content_plan'] = content_plan

        # Format and display content plan
        formatted_plan = "📋 Контент-план на 14 дней:\n\n"
        for i, post in enumerate(content_plan.split('\n\n'), 1):
            if post.strip():
                formatted_plan += f"📝 Пост #{i}:\n{post}\n\n"

        # Split long message if needed
        if len(formatted_plan) > 4000:
            # Send plan in parts
            for i in range(0, len(formatted_plan), 4000):
                message.reply_text(formatted_plan[i:i+4000])
        else:
            message.reply_text(formatted_plan)

        # Show options for post generation
        message.reply_text(
            "✍️ Чтобы сгенерировать полный текст поста, "
            "введите его номер (от 1 до 14):",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Сгенерировать новый контент-план", 
                                   callback_data='new_plan')
            ]])
        )

        context.user_data['waiting_for'] = 'post_number'
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error generating content plan: {e}")
        message = update.callback_query.message if update.callback_query else update.message
        message.reply_text(
            "❌ Произошла ошибка при генерации контент-плана. "
            "Попробуйте еще раз позже."
        )
        return ConversationHandler.END

def button_handler(update: Update, context: CallbackContext) -> int:
    """Handle button clicks during conversation."""
    query = update.callback_query
    query.answer()

    logger.info(f"Button pressed: {query.data}")
    logger.info(f"Current user_data: {context.user_data}")
    logger.info(f"Current waiting_for: {context.user_data.get('waiting_for')}")

    if query.data == 'start_work':
        query.message.reply_text("Какая тема вашего канала?")
        context.user_data['waiting_for'] = 'topic'
        return TOPIC

    if query.data in ['advertising', 'products', 'services', 'consulting']:
        context.user_data['monetization'] = query.data
        if query.data != 'advertising':
            query.message.reply_text("Опишите ваш продукт/услугу/курс подробнее:")
            context.user_data['waiting_for'] = 'product_details'
            return PRODUCT_DETAILS
        else:
            query.message.reply_text("Какие у вас есть дополнительные пожелания к контенту?")
            context.user_data['waiting_for'] = 'preferences'
            return PREFERENCES

    if query.data in ['aggressive', 'business', 'humorous', 'custom']:
        context.user_data['style'] = query.data
        if query.data == 'custom':
            query.message.reply_text("Опишите ваш стиль:")
            context.user_data['waiting_for'] = 'custom_style'
            return STYLE
        query.message.reply_text("Какие эмоции должен вызывать контент у аудитории?")
        context.user_data['waiting_for'] = 'emotions'
        return EMOTIONS

    if query.data == 'continue_after_example':
        logger.info("Processing continue_after_example")
        examples_count = len(context.user_data.get('examples', []))
        logger.info(f"Current examples count: {examples_count}")

        if examples_count < 2:
            query.message.reply_text(
                "Отправьте еще один пример поста:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Еще пример поста", callback_data='continue_after_example'),
                    InlineKeyboardButton("Готово", callback_data='finish_examples')
                ]])
            )
            return EXAMPLES
        else:
            return process_examples(update, context)

    if query.data == 'finish_examples':
        logger.info("Processing finish_examples")
        return process_examples(update, context)

    return ConversationHandler.END

def text_handler(update: Update, context: CallbackContext) -> int:
    """Handle text input during conversation."""
    text = update.message.text
    logger.info(f"Received text: {text}")
    logger.info(f"Current waiting_for: {context.user_data.get('waiting_for')}")

    if context.user_data.get('waiting_for') == 'post_number':
        try:
            post_number = int(text)
            if 1 <= post_number <= 14:
                update.message.reply_text("🔄 Генерирую пост...")
                generated_post = generate_post(context.user_data, post_number)
                update.message.reply_text(
                    f"✨ Готово! Вот ваш пост #{post_number}:\n\n{generated_post}\n\n"
                    "Чтобы сгенерировать другой пост, введите его номер (1-14):",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔄 Сгенерировать новый контент-план", 
                                           callback_data='new_plan')
                    ]])
                )
                return ConversationHandler.END
            else:
                update.message.reply_text(
                    "❌ Пожалуйста, введите число от 1 до 14."
                )
                return ConversationHandler.END
        except ValueError:
            update.message.reply_text(
                "❌ Пожалуйста, введите корректный номер поста (число от 1 до 14)."
            )
            return ConversationHandler.END

    elif context.user_data.get('waiting_for') == 'examples':
        logger.info(f"Processing example post #{len(context.user_data.get('examples', []))}")
        # Add the example to the list
        if 'examples' not in context.user_data:
            context.user_data['examples'] = []
        context.user_data['examples'].append(text)

        # Show confirmation and buttons
        keyboard = [[
            InlineKeyboardButton("Еще пример поста", callback_data='continue_after_example'),
            InlineKeyboardButton("Готово", callback_data='finish_examples')
        ]]
        update.message.reply_text(
            f"✅ Пример поста #{len(context.user_data['examples'])} получен!\n\n"
            "Отправьте еще один пример поста или нажмите 'Готово', "
            "если хотите продолжить.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EXAMPLES

    elif context.user_data.get('waiting_for') == 'emotions':
        context.user_data['emotions'] = text
        context.user_data['examples'] = []  # Initialize empty list for examples
        keyboard = [[
            InlineKeyboardButton("Еще пример поста", callback_data='continue_after_example'),
            InlineKeyboardButton("Готово", callback_data='finish_examples')
        ]]
        update.message.reply_text(
            "Отправьте пример поста, который вам нравится.\n"
            "После отправки поста нажмите 'Еще пример поста' для отправки следующего примера\n"
            "или 'Готово', если хотите продолжить.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['waiting_for'] = 'examples'
        return EXAMPLES

    elif context.user_data.get('waiting_for') == 'topic':
        context.user_data['topic'] = text
        update.message.reply_text("Опишите вашу целевую аудиторию:")
        context.user_data['waiting_for'] = 'audience'
        return AUDIENCE

    elif context.user_data.get('waiting_for') == 'audience':
        context.user_data['audience'] = text
        keyboard = create_monetization_keyboard()
        update.message.reply_text(
            "Выберите метод монетизации:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return MONETIZATION

    elif context.user_data.get('waiting_for') == 'product_details':
        context.user_data['product_details'] = text
        update.message.reply_text("Какие у вас есть дополнительные пожелания к контенту?")
        context.user_data['waiting_for'] = 'preferences'
        return PREFERENCES

    elif context.user_data.get('waiting_for') == 'preferences':
        context.user_data['preferences'] = text
        keyboard = create_style_keyboard()
        update.message.reply_text(
            "Выберите стиль написания:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return STYLE

    elif context.user_data.get('waiting_for') == 'custom_style':
        context.user_data['style'] = text
        update.message.reply_text("Какие эмоции должен вызывать контент у аудитории?")
        context.user_data['waiting_for'] = 'emotions'
        return EMOTIONS

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    update.message.reply_text('Операция отменена. Для начала напишите /start')
    return ConversationHandler.END