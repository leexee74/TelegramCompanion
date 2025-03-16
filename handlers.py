import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
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

async def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and check subscription."""
    try:
        logger.info(f"Start command received from user {update.effective_user.id}")

        is_subscribed = await check_subscription(context, update.effective_user.id)
        logger.info(f"Subscription check result for user {update.effective_user.id}: {is_subscribed}")

        if not is_subscribed:
            logger.info("User not subscribed, sending subscription prompt")
            await update.message.reply_text(
                "👋 Для использования бота необходимо подписаться на канал @expert_buyanov",
                reply_markup=create_subscription_keyboard()
            )
            return SUBSCRIPTION_CHECK

        logger.info("User is subscribed, proceeding with conversation")
        return await start_work(update, context)
    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже или свяжитесь с администратором."
        )
        return ConversationHandler.END

async def start_work(update: Update, context: CallbackContext) -> int:
    """Start the work after subscription check."""
    try:
        keyboard = [[InlineKeyboardButton("Начать работу", callback_data='start_work')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = update.message or update.callback_query.message
        await message.reply_text(
            "Добро пожаловать! Я помогу вам создать engaging посты для вашего Telegram канала.",
            reply_markup=reply_markup
        )
        return TOPIC
    except Exception as e:
        logger.error(f"Error in start_work: {e}", exc_info=True)
        message = update.message or update.callback_query.message
        await message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

async def button_handler(update: Update, context: CallbackContext) -> int:
    """Handle button clicks during conversation."""
    query = update.callback_query
    query.answer()

    logger.info(f"Button pressed: {query.data}")
    logger.info(f"Current user_data: {context.user_data}")
    logger.info(f"Current waiting_for: {context.user_data.get('waiting_for')}")

    if query.data == 'check_subscription':
        is_subscribed = await check_subscription(context, update.effective_user.id)
        if is_subscribed:
            return await start_work(update, context)
        else:
            await query.message.reply_text(
                "❌ Вы все еще не подписаны на канал @expert_buyanov\n"
                "Подпишитесь и нажмите кнопку проверки ещё раз.",
                reply_markup=create_subscription_keyboard()
            )
            return SUBSCRIPTION_CHECK

    if query.data == 'start_work':
        await query.message.reply_text("Какая тема вашего канала?")
        context.user_data.clear()  # Clear previous data
        context.user_data['waiting_for'] = 'topic'
        return TOPIC

    if query.data == 'new_plan':
        await query.message.reply_text("Какая тема вашего канала?")
        context.user_data.clear()  # Clear previous data
        context.user_data['waiting_for'] = 'topic'
        return TOPIC

    if query.data in ['advertising', 'products', 'services', 'consulting']:
        context.user_data['monetization'] = query.data
        if query.data != 'advertising':
            await query.message.reply_text("Опишите ваш продукт/услугу/курс подробнее:")
            context.user_data['waiting_for'] = 'product_details'
            return PRODUCT_DETAILS
        else:
            await query.message.reply_text("Какие у вас есть дополнительные пожелания к контенту?")
            context.user_data['waiting_for'] = 'preferences'
            return PREFERENCES

    if query.data in ['aggressive', 'business', 'humorous', 'custom']:
        context.user_data['style'] = query.data
        if query.data == 'custom':
            await query.message.reply_text("Опишите ваш стиль:")
            context.user_data['waiting_for'] = 'custom_style'
            return STYLE
        await query.message.reply_text("Какие эмоции должен вызывать контент у аудитории?")
        context.user_data['waiting_for'] = 'emotions'
        return EMOTIONS

    return await process_examples(update, context)


async def text_handler(update: Update, context: CallbackContext) -> int:
    """Handle text input during conversation."""
    try:
        text = update.message.text
        logger.info(f"Received text: {text}")
        logger.info(f"Current waiting_for: {context.user_data.get('waiting_for')}")
        logger.info(f"Current user_data: {context.user_data}")

        if context.user_data.get('waiting_for') == 'post_number':
            logger.info("Processing post number input")
            try:
                post_number = int(text)
                logger.info(f"Attempting to generate post #{post_number}")

                if 1 <= post_number <= 14:
                    # Send immediate confirmation
                    await update.message.reply_text(f"🔄 Получено число {post_number}, генерирую пост...")

                    try:
                        # Get saved user data
                        user_data = get_user_data(update.effective_chat.id)
                        logger.info(f"Retrieved user data from database: {user_data}")

                        if not user_data or 'content_plan' not in user_data:
                            logger.error("No content plan found in user data")
                            await update.message.reply_text(
                                "❌ Ошибка: контент-план не найден. Пожалуйста, начните заново с команды /start"
                            )
                            return ConversationHandler.END

                        # Generate post
                        logger.info("Calling generate_post function")
                        generated_post = generate_post(user_data, post_number)
                        logger.info(f"Successfully generated post #{post_number}")

                        # Send response
                        await update.message.reply_text(
                            f"✨ Готово! Вот ваш пост #{post_number}:\n\n{generated_post}\n\n"
                            "Чтобы сгенерировать другой пост, введите его номер (1-14):",
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton("🔄 Сгенерировать новый контент-план", 
                                                callback_data='new_plan')
                            ]])
                        )
                        return POST_NUMBER

                    except Exception as e:
                        logger.error(f"Error generating post: {e}")
                        await update.message.reply_text(
                            "❌ Произошла ошибка при генерации поста. "
                            "Пожалуйста, попробуйте еще раз или выберите другой номер поста."
                        )
                        return POST_NUMBER
                else:
                    await update.message.reply_text(
                        "❌ Пожалуйста, введите число от 1 до 14."
                    )
                    return POST_NUMBER
            except ValueError:
                await update.message.reply_text(
                    "❌ Пожалуйста, введите корректный номер поста (число от 1 до 14)."
                )
                return POST_NUMBER

        elif context.user_data.get('waiting_for') == 'topic':
            context.user_data['topic'] = text
            await update.message.reply_text("Опишите вашу целевую аудиторию:")
            context.user_data['waiting_for'] = 'audience'
            return AUDIENCE

        elif context.user_data.get('waiting_for') == 'audience':
            context.user_data['audience'] = text
            keyboard = create_monetization_keyboard()
            await update.message.reply_text(
                "Выберите метод монетизации:",
                reply_markup=keyboard
            )
            return MONETIZATION

        elif context.user_data.get('waiting_for') == 'product_details':
            context.user_data['product_details'] = text
            await update.message.reply_text("Какие у вас есть дополнительные пожелания к контенту?")
            context.user_data['waiting_for'] = 'preferences'
            return PREFERENCES

        elif context.user_data.get('waiting_for') == 'preferences':
            context.user_data['preferences'] = text
            keyboard = create_style_keyboard()
            await update.message.reply_text(
                "Выберите стиль написания:",
                reply_markup=keyboard
            )
            return STYLE

        elif context.user_data.get('waiting_for') == 'custom_style':
            context.user_data['style'] = text
            await update.message.reply_text("Какие эмоции должен вызывать контент у аудитории?")
            context.user_data['waiting_for'] = 'emotions'
            return EMOTIONS

        elif context.user_data.get('waiting_for') == 'emotions':
            context.user_data['emotions'] = text
            return await process_examples(update, context)

    except Exception as e:
        logger.error(f"Error in text_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, попробуйте еще раз или начните заново с команды /start"
        )
        return ConversationHandler.END

async def process_examples(update: Update, context: CallbackContext) -> int:
    """Process collected examples and generate content plan."""
    try:
        logger.info("Processing examples with data: %s", context.user_data)

        # Show processing message
        message = update.callback_query.message if update.callback_query else update.message
        await message.reply_text("🔄 Генерирую контент-план на 14 дней...")

        # Generate and save content plan
        logger.info("Generating content plan...")
        content_plan = generate_content_plan(context.user_data)
        logger.info(f"Generated content plan: {content_plan}")

        context.user_data['content_plan'] = content_plan
        save_user_data(update.effective_chat.id, context.user_data)
        logger.info("Saved content plan to database")

        # Format and display content plan
        formatted_plan = "📋 Контент-план на 14 дней:\n\n"
        formatted_plan += content_plan

        # Split long message if needed
        if len(formatted_plan) > 4000:
            # Send plan in parts
            parts = [formatted_plan[i:i+4000] for i in range(0, len(formatted_plan), 4000)]
            for part in parts:
                await message.reply_text(part)
        else:
            await message.reply_text(formatted_plan)

        # Show options for post generation
        await message.reply_text(
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
        logger.info("Entering post number input state with data: %s", context.user_data)
        return POST_NUMBER

    except Exception as e:
        logger.error(f"Error generating content plan: {e}")
        message = update.callback_query.message if update.callback_query else update.message
        await message.reply_text(
            "❌ Произошла ошибка при генерации контент-плана. "
            "Попробуйте еще раз позже."
        )
        return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    await update.message.reply_text('Операция отменена. Для начала напишите /start')
    return ConversationHandler.END