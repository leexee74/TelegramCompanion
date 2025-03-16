import logging
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import save_user_data, get_user_data
from prompts import generate_content_plan, generate_post
from utils import (
    create_monetization_keyboard, create_style_keyboard,
    create_subscription_keyboard, check_subscription
)

logger = logging.getLogger(__name__)

# Conversation states
(SUBSCRIPTION_CHECK, TOPIC, AUDIENCE, MONETIZATION, PRODUCT_DETAILS, 
 PREFERENCES, STYLE, EMOTIONS, EXAMPLES, POST_NUMBER) = range(10)

def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and check subscription."""
    try:
        user_id = update.effective_user.id
        logger.info(f"============ START COMMAND ============")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Chat ID: {update.effective_chat.id}")
        logger.info("=======================================")

        # Check subscription status
        is_subscribed = check_subscription(context, user_id)
        logger.info(f"Subscription check result for user {user_id}: {is_subscribed}")

        if not is_subscribed:
            reply_markup = create_subscription_keyboard()
            update.message.reply_text(
                "👋 Для использования бота необходимо подписаться на канал @expert_buyanov",
                reply_markup=reply_markup
            )
            return SUBSCRIPTION_CHECK

        return start_work(update, context)

    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

def start_work(update: Update, context: CallbackContext) -> int:
    """Start the work after subscription check."""
    try:
        message = update.message or update.callback_query.message
        keyboard = [[InlineKeyboardButton("Начать работу", callback_data='start_work')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message.reply_text(
            "Добро пожаловать! Я помогу вам создать engaging посты для вашего Telegram канала.",
            reply_markup=reply_markup
        )
        return TOPIC

    except Exception as e:
        logger.error(f"Error in start_work: {e}", exc_info=True)
        message = update.message or update.callback_query.message
        message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

def button_handler(update: Update, context: CallbackContext) -> int:
    """Handle button callbacks."""
    query = update.callback_query
    query.answer()

    logger.info("============ BUTTON PRESSED ============")
    logger.info(f"Button data: {query.data}")
    logger.info(f"Current state: {context.user_data.get('waiting_for')}")
    logger.info(f"User data: {context.user_data}")
    logger.info("=======================================")

    try:
        if query.data == 'check_subscription':
            is_subscribed = check_subscription(context, update.effective_user.id)
            if is_subscribed:
                return start_work(update, context)
            else:
                query.message.reply_text(
                    "❌ Вы все еще не подписаны на канал @expert_buyanov\n"
                    "Подпишитесь и нажмите кнопку проверки ещё раз.",
                    reply_markup=create_subscription_keyboard()
                )
                return SUBSCRIPTION_CHECK

        elif query.data == 'start_work':
            query.message.reply_text("Какая тема вашего канала?")
            context.user_data.clear()
            context.user_data['waiting_for'] = 'topic'
            return TOPIC

        elif query.data in ['advertising', 'products', 'services', 'consulting']:
            context.user_data['monetization'] = query.data
            if query.data != 'advertising':
                query.message.reply_text("Опишите ваш продукт/услугу/курс подробнее:")
                context.user_data['waiting_for'] = 'product_details'
                return PRODUCT_DETAILS
            else:
                query.message.reply_text("Какие у вас есть дополнительные пожелания к контенту?")
                context.user_data['waiting_for'] = 'preferences'
                return PREFERENCES

        elif query.data in ['aggressive', 'business', 'humorous', 'custom']:
            context.user_data['style'] = query.data
            if query.data == 'custom':
                query.message.reply_text("Опишите ваш стиль:")
                context.user_data['waiting_for'] = 'custom_style'
                return STYLE

            query.message.reply_text("Какие эмоции должен вызывать контент у аудитории?")
            context.user_data['waiting_for'] = 'emotions'
            return EMOTIONS

        elif query.data == 'new_plan':
            query.message.reply_text("Какая тема вашего канала?")
            context.user_data.clear()
            context.user_data['waiting_for'] = 'topic'
            return TOPIC

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error in button_handler: {e}", exc_info=True)
        query.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
        )
        return ConversationHandler.END

def text_handler(update: Update, context: CallbackContext) -> int:
    """Handle text input during conversation."""
    try:
        text = update.message.text
        logger.info("============ TEXT RECEIVED ============")
        logger.info(f"Text: {text}")
        logger.info(f"Waiting for: {context.user_data.get('waiting_for')}")
        logger.info(f"User data: {context.user_data}")
        logger.info("======================================")

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
                reply_markup=keyboard
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
                reply_markup=keyboard
            )
            return STYLE

        elif context.user_data.get('waiting_for') == 'custom_style':
            context.user_data['style'] = text
            update.message.reply_text("Какие эмоции должен вызывать контент у аудитории?")
            context.user_data['waiting_for'] = 'emotions'
            return EMOTIONS

        elif context.user_data.get('waiting_for') == 'emotions':
            context.user_data['emotions'] = text
            update.message.reply_text(
                "Отлично! Теперь перешлите мне 2-3 примера постов, которые вам нравятся.\n"
                "После отправки всех примеров, я сгенерирую контент-план."
            )
            context.user_data['waiting_for'] = 'examples'
            context.user_data['examples'] = []
            return EXAMPLES

        elif context.user_data.get('waiting_for') == 'examples':
            if 'examples' not in context.user_data:
                context.user_data['examples'] = []

            context.user_data['examples'].append(text)
            if len(context.user_data['examples']) >= 2:
                return process_examples(update, context)
            else:
                update.message.reply_text("Отлично! Пришлите еще один пример.")
                return EXAMPLES

        elif context.user_data.get('waiting_for') == 'post_number':
            try:
                post_number = int(text)
                if 1 <= post_number <= 14:
                    update.message.reply_text(f"🔄 Получено число {post_number}, генерирую пост...")
                    user_data = get_user_data(update.effective_chat.id)

                    if not user_data or 'content_plan' not in user_data:
                        update.message.reply_text(
                            "❌ Ошибка: контент-план не найден. Пожалуйста, начните заново с команды /start"
                        )
                        return ConversationHandler.END

                    generated_post = generate_post(user_data, post_number)
                    update.message.reply_text(
                        f"✨ Готово! Вот ваш пост #{post_number}:\n\n{generated_post}\n\n"
                        "Чтобы сгенерировать другой пост, введите его номер (1-14):",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔄 Сгенерировать новый контент-план", 
                                             callback_data='new_plan')
                        ]])
                    )
                    return POST_NUMBER
                else:
                    update.message.reply_text("❌ Пожалуйста, введите число от 1 до 14.")
                    return POST_NUMBER
            except ValueError:
                update.message.reply_text(
                    "❌ Пожалуйста, введите корректный номер поста (число от 1 до 14)."
                )
                return POST_NUMBER

    except Exception as e:
        logger.error(f"Error in text_handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, попробуйте еще раз или начните заново с команды /start"
        )
        return ConversationHandler.END

def process_examples(update: Update, context: CallbackContext) -> int:
    """Process collected examples and generate content plan."""
    try:
        logger.info("============ PROCESSING EXAMPLES ============")
        logger.info(f"User data: {context.user_data}")
        logger.info("===========================================")

        # Show processing message
        update.message.reply_text("🔄 Генерирую контент-план на 14 дней...")

        # Generate and save content plan
        content_plan = generate_content_plan(context.user_data)
        context.user_data['content_plan'] = content_plan
        save_user_data(update.effective_chat.id, context.user_data)

        # Format and display content plan
        formatted_plan = "📋 Контент-план на 14 дней:\n\n"
        formatted_plan += content_plan

        # Split long message if needed
        if len(formatted_plan) > 4000:
            # Send plan in parts
            parts = [formatted_plan[i:i+4000] for i in range(0, len(formatted_plan), 4000)]
            for part in parts:
                update.message.reply_text(part)
        else:
            update.message.reply_text(formatted_plan)

        # Show options for post generation
        update.message.reply_text(
            "✍️ Чтобы сгенерировать полный текст поста, "
            "введите его номер (от 1 до 14):",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Сгенерировать новый контент-план", 
                                 callback_data='new_plan')
            ]])
        )

        # Set state for post number input
        context.user_data['waiting_for'] = 'post_number'
        save_user_data(update.effective_chat.id, context.user_data)
        return POST_NUMBER

    except Exception as e:
        logger.error(f"Error generating content plan: {e}")
        update.message.reply_text(
            "❌ Произошла ошибка при генерации контент-плана. "
            "Попробуйте еще раз позже."
        )
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    update.message.reply_text('Операция отменена. Для начала напишите /start')
    return ConversationHandler.END