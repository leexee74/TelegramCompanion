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

def button_handler(update: Update, context: CallbackContext) -> int:
    """Handle button clicks during conversation."""
    query = update.callback_query
    query.answer()

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
            context.user_data['waiting_for'] = 'style'
            return STYLE
        query.message.reply_text("Какие эмоции должен вызывать контент у аудитории?")
        context.user_data['waiting_for'] = 'emotions'
        return EMOTIONS

    # Default return if no other conditions are met
    return ConversationHandler.END

def text_handler(update: Update, context: CallbackContext) -> int:
    """Handle text input during conversation."""
    text = update.message.text

    if not hasattr(context, 'user_data'):
        context.user_data = {}

    # Handle different states
    if context.user_data.get('waiting_for') == 'topic':
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

    elif context.user_data.get('waiting_for') == 'emotions':
        context.user_data['emotions'] = text
        update.message.reply_text("Перешлите 2-3 примера постов, которые вам нравятся:")
        context.user_data['waiting_for'] = 'examples'
        return EXAMPLES

    elif context.user_data.get('waiting_for') == 'examples':
        context.user_data['examples'] = text
        # Generate sample post
        try:
            sample_post = generate_post(context.user_data)
            update.message.reply_text(
                "Вот пример поста:\n\n" + sample_post + "\n\nГенерирую контент-план..."
            )
            content_plan = generate_content_plan(context.user_data)
            context.user_data['content_plan'] = content_plan
            save_user_data(update.effective_chat.id, context.user_data)

            keyboard = [
                [InlineKeyboardButton("📋 Просмотреть контент-план", callback_data='view_plan')],
                [InlineKeyboardButton("✍ Создать пост", callback_data='create_post')],
                [InlineKeyboardButton("🔄 Сгенерировать новый контент-план", callback_data='new_plan')]
            ]
            update.message.reply_text(
                "Контент-план готов! Что делаем дальше?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            update.message.reply_text(
                "Произошла ошибка при генерации контента. Попробуйте еще раз позже."
            )
            return ConversationHandler.END

    # Default return if no other conditions are met
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    update.message.reply_text('Операция отменена. Для начала напишите /start')
    return ConversationHandler.END