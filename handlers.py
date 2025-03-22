import logging
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import (
    save_user_preferences, get_user_preferences,
    save_scheduled_message, get_scheduled_messages, save_user_data, get_user_data
)
from prompts import generate_content_plan, generate_post, generate_product_repackaging
from utils import (
    create_monetization_keyboard, create_style_keyboard,
    create_subscription_keyboard, create_main_menu_keyboard,
    create_back_to_menu_keyboard, check_subscription
)

logger = logging.getLogger(__name__)

# Conversation states
(SUBSCRIPTION_CHECK, MAIN_MENU, TOPIC, AUDIENCE, MONETIZATION, PRODUCT_DETAILS, 
 PREFERENCES, STYLE, EMOTIONS, EXAMPLES, POST_NUMBER,
 REPACKAGE_AUDIENCE, REPACKAGE_TOOL, REPACKAGE_RESULT) = range(14)

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
            logger.info("Sending subscription check message")
            update.message.reply_text(
                "👋 Для использования бота необходимо подписаться на канал @expert_buyanov",
                reply_markup=reply_markup
            )
            return SUBSCRIPTION_CHECK

        # Show main menu
        main_menu_keyboard = create_main_menu_keyboard()
        logger.info(f"Created main menu keyboard: {main_menu_keyboard.to_dict()}")
        update.message.reply_text(
            "👋 Добро пожаловать! Выберите действие:",
            reply_markup=main_menu_keyboard
        )
        context.user_data.clear()
        logger.info("Cleared user data and sent main menu")
        return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

def handle_main_menu(update: Update, context: CallbackContext) -> int:
    """Handle main menu selection."""
    query = update.callback_query
    query.answer()

    try:
        if query.data == 'content_plan':
            query.message.reply_text(
                "📝 Какая тема вашего канала?\n\n"
                "Опишите основную тематику и направленность канала.\n"
                "Например: бизнес, психология, здоровье, технологии и т.д."
            )
            context.user_data['waiting_for'] = 'topic'
            return TOPIC

        elif query.data == 'repackage':
            query.message.reply_text(
                "👥 Кто твоя аудитория?\n\n"
                "Например: предприниматели и блоггеры, которые продают товар или услугу"
            )
            context.user_data['waiting_for'] = 'repackage_audience'
            return REPACKAGE_AUDIENCE

        elif query.data == 'start_over':
            context.user_data.clear()
            query.message.reply_text(
                "🔄 Настройки сброшены. Выберите действие:",
                reply_markup=create_main_menu_keyboard()
            )
            return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in main menu handler: {e}", exc_info=True)
        query.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
        )
        return ConversationHandler.END

def handle_repackage_audience(update: Update, context: CallbackContext) -> int:
    """Handle product repackaging audience input."""
    try:
        context.user_data['repackage_audience'] = update.message.text
        update.message.reply_text(
            "🛠️ Какой инструмент ты даешь?\n\n"
            "Например: как снять рилс на 1 млн просмотров",
            reply_markup=create_back_to_menu_keyboard()
        )
        return REPACKAGE_TOOL
    except Exception as e:
        logger.error(f"Error in repackage audience handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
        )
        return ConversationHandler.END

def handle_repackage_tool(update: Update, context: CallbackContext) -> int:
    """Handle product repackaging tool input."""
    try:
        context.user_data['repackage_tool'] = update.message.text
        update.message.reply_text(
            "🎯 Какой результат они получат?\n\n"
            "Например: рилс с 1 млн просмотров принесет продажи",
            reply_markup=create_back_to_menu_keyboard()
        )
        return REPACKAGE_RESULT
    except Exception as e:
        logger.error(f"Error in repackage tool handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
        )
        return ConversationHandler.END

def handle_repackage_result(update: Update, context: CallbackContext) -> int:
    """Generate product repackaging content."""
    try:
        context.user_data['repackage_result'] = update.message.text

        # Generate repackaging content
        repackaging_data = {
            'audience': context.user_data['repackage_audience'],
            'tool': context.user_data['repackage_tool'],
            'result': context.user_data['repackage_result']
        }

        update.message.reply_text("🔄 Генерирую переупаковку продукта...")

        content = generate_product_repackaging(repackaging_data)

        # Send the generated content
        update.message.reply_text(
            f"{content}\n\n"
            "Выберите следующее действие:",
            reply_markup=create_main_menu_keyboard()
        )
        return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in repackage result handler: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
        )
        return ConversationHandler.END

def button_handler(update: Update, context: CallbackContext) -> int:
    """Handle button callbacks."""
    query = update.callback_query
    query.answer()

    logger.info("============ BUTTON PRESSED ============")
    logger.info(f"Button data: {query.data}")
    logger.info(f"Current state: {context.user_data.get('waiting_for')}")
    logger.info(f"User data keys: {list(context.user_data.keys())}")
    logger.info("=======================================")

    try:
        # Handle subscription check
        if query.data == 'check_subscription':
            is_subscribed = check_subscription(context, update.effective_user.id)
            if is_subscribed:
                query.message.reply_text(
                    "✅ Отлично! Теперь можно начать работу.\n\n"
                    "Выберите действие:",
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

        elif query.data == 'back_to_menu':
            query.message.reply_text("Вы вернулись в главное меню.", reply_markup=create_main_menu_keyboard())
            return MAIN_MENU


        # Handle start work button (moved to main menu)
        elif query.data == 'start_work': #This is redundant now.
            query.message.reply_text(
                "📝 Какая тема вашего канала?\n\n"
                "Опишите основную тематику и направленность канала.\n"
                "Например: бизнес, психология, здоровье, технологии и т.д.\n\n"
                "Напишите краткое описание темы:"
            )
            context.user_data['waiting_for'] = 'topic'
            logger.info("Requested channel topic")
            return TOPIC

        # Handle monetization options
        elif query.data in ['advertising', 'products', 'services', 'consulting']:
            context.user_data['monetization'] = query.data
            if query.data != 'advertising':
                query.message.reply_text(
                    "🎯 Опишите ваш продукт/услугу/курс подробнее:\n\n"
                    "Укажите основные характеристики, преимущества и особенности."
                )
                context.user_data['waiting_for'] = 'product_details'
                return PRODUCT_DETAILS
            else:
                query.message.reply_text(
                    "🎯 Какие у вас есть дополнительные пожелания к контенту?\n\n"
                    "Например:\n"
                    "• Особый формат подачи\n"
                    "• Специфические темы\n"
                    "• Табу и ограничения"
                )
                context.user_data['waiting_for'] = 'preferences'
                return PREFERENCES

        # Handle writing style selection
        elif query.data in ['aggressive', 'business', 'humorous', 'custom']:
            context.user_data['style'] = query.data
            if query.data == 'custom':
                query.message.reply_text(
                    "✍ Опишите ваш стиль:\n\n"
                    "Укажите особенности подачи материала, тон общения и другие важные детали."
                )
                context.user_data['waiting_for'] = 'custom_style'
                return STYLE

            query.message.reply_text(
                "🎭 Какие эмоции должен вызывать контент у аудитории?\n\n"
                "Например:\n"
                "• Доверие\n"
                "• Интерес\n"
                "• Желание действовать"
            )
            context.user_data['waiting_for'] = 'emotions'
            return EMOTIONS

        # Handle add example
        elif query.data == 'add_example':
            logger.info("User requested to add another example")
            query.message.reply_text("📝 Хорошо, пришлите следующий пример поста.")
            return EXAMPLES

        # Handle finish examples
        elif query.data == 'finish_examples':
            logger.info("User requested to finish adding examples")
            if not context.user_data.get('examples', []):
                query.message.reply_text(
                    "❌ Пожалуйста, пришлите хотя бы один пример поста."
                )
                return EXAMPLES

            try:
                # Verify all required data is present
                required_fields = ['topic', 'audience', 'monetization', 'style', 'emotions']
                missing_fields = [field for field in required_fields if not context.user_data.get(field)]

                if missing_fields:
                    logger.error(f"Missing required fields: {missing_fields}")
                    query.message.reply_text(
                        "❌ Не хватает некоторых данных. Пожалуйста, начните заново с команды /start"
                    )
                    return ConversationHandler.END

                query.message.reply_text("🔄 Генерирую контент-план на 14 дней...")

                # Extract text from examples
                examples_text = [example['text'] for example in context.user_data.get('examples', [])]
                context.user_data['examples_text'] = examples_text

                # Generate and save content plan
                content_plan = generate_content_plan(context.user_data)
                context.user_data['content_plan'] = content_plan
                save_user_data(update.effective_chat.id, context.user_data)

                # Format and display content plan
                formatted_plan = "📋 Контент-план на 14 дней:\n\n"
                formatted_plan += content_plan

                # Split long message if needed
                if len(formatted_plan) > 4000:
                    parts = [formatted_plan[i:i+4000] for i in range(0, len(formatted_plan), 4000)]
                    for part in parts:
                        query.message.reply_text(part)
                else:
                    query.message.reply_text(formatted_plan)

                # Show options for post generation
                query.message.reply_text(
                    "✍️ Чтобы сгенерировать полный текст поста, "
                    "введите его номер (от 1 до 14):",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔄 Сгенерировать новый контент-план", 
                                           callback_data='new_plan')
                    ]])
                )
                context.user_data['waiting_for'] = 'post_number'
                return POST_NUMBER

            except Exception as e:
                logger.exception("Error in finish_examples:")
                query.message.reply_text(
                    "❌ Произошла ошибка при генерации контент-плана. "
                    "Пожалуйста, попробуйте еще раз или начните заново с команды /start"
                )
                return EXAMPLES

        # Handle new plan request
        elif query.data == 'new_plan':
            logger.info("User requested new content plan")
            query.message.reply_text("📝 Какая тема вашего канала?")
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

def handle_example_post(update: Update, context: CallbackContext) -> int:
    """Handle incoming example posts and show action buttons."""
    try:
        logger.info("============ HANDLING EXAMPLE POST ============")

        # Extract text from either forwarded or regular message
        if update.message.forward_from_chat:
            # This is a forwarded message from a channel
            text = update.message.text or update.message.caption or ''
            source = f"(переслано из {update.message.forward_from_chat.title})"
            logger.info(f"Received forwarded post from channel: {update.message.forward_from_chat.title}")
        else:
            # Regular text message
            text = update.message.text
            source = ""
            logger.info("Received direct text message")

        logger.info(f"Post content: {text[:50]}...")  # Log first 50 chars

        # Initialize examples list if it doesn't exist
        if 'examples' not in context.user_data:
            context.user_data['examples'] = []
            logger.info("Initialized examples list")

        # Add the new example with source information
        example = {'text': text, 'source': source}
        context.user_data['examples'].append(example)
        example_count = len(context.user_data['examples'])
        logger.info(f"Added example post #{example_count}")

        # Create keyboard with buttons
        keyboard = [[
            InlineKeyboardButton("📝 Добавить еще пост", callback_data='add_example'),
            InlineKeyboardButton("✅ Готово", callback_data='finish_examples')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send response with buttons
        update.message.reply_text(
            f"👍 Отлично! Пост #{example_count} {source} сохранен.\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
        logger.info("Sent response with action buttons")
        return EXAMPLES

    except Exception as e:
        logger.error(f"Error handling example post: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Произошла ошибка при сохранении примера. "
            "Пожалуйста, попробуйте еще раз."
        )
        return EXAMPLES

def text_handler(update: Update, context: CallbackContext) -> int:
    """Handle text input during conversation."""
    try:
        text = update.message.text
        logger.info("============ TEXT RECEIVED ============")
        logger.info(f"Text: {text}")
        logger.info(f"Current state: {context.user_data.get('waiting_for')}")
        logger.info(f"User data keys: {list(context.user_data.keys())}")
        logger.info("======================================")

        if context.user_data.get('waiting_for') == 'examples':
            return handle_example_post(update, context)

        elif context.user_data.get('waiting_for') == 'topic':
            logger.info("Processing topic input")
            context.user_data['topic'] = text
            update.message.reply_text(
                "✍️ Отлично! Теперь опишите вашу целевую аудиторию:\n\n"
                "Например:\n"
                "• Возраст\n"
                "• Интересы\n"
                "• Проблемы, которые вы решаете"
            )
            context.user_data['waiting_for'] = 'audience'
            logger.info("Topic saved, moving to audience input")
            return AUDIENCE

        elif context.user_data.get('waiting_for') == 'audience':
            logger.info("Processing audience input")
            context.user_data['audience'] = text
            keyboard = create_monetization_keyboard()
            update.message.reply_text(
                "💰 Выберите метод монетизации:",
                reply_markup=keyboard
            )
            logger.info("Audience saved, moving to monetization selection")
            return MONETIZATION

        elif context.user_data.get('waiting_for') == 'product_details':
            logger.info("Processing product details input")
            context.user_data['product_details'] = text
            update.message.reply_text(
                "🎯 Какие у вас есть дополнительные пожелания к контенту?\n\n"
                "Например:\n"
                "• Особый формат подачи\n"
                "• Специфические темы\n"
                "• Табу и ограничения"
            )
            context.user_data['waiting_for'] = 'preferences'
            logger.info("Product details saved, moving to preferences input")
            return PREFERENCES

        elif context.user_data.get('waiting_for') == 'preferences':
            logger.info("Processing preferences input")
            context.user_data['preferences'] = text
            keyboard = create_style_keyboard()
            update.message.reply_text(
                "✨ Выберите стиль написания постов:",
                reply_markup=keyboard
            )
            logger.info("Preferences saved, moving to style selection")
            return STYLE

        elif context.user_data.get('waiting_for') == 'custom_style':
            logger.info("Processing custom style input")
            context.user_data['style'] = text
            update.message.reply_text(
                "🎭 Какие эмоции должен вызывать контент у аудитории?\n\n"
                "Например:\n"
                "• Доверие\n"
                "• Интерес\n"
                "• Желание действовать"
            )
            context.user_data['waiting_for'] = 'emotions'
            logger.info("Custom style saved, moving to emotions input")
            return EMOTIONS

        elif context.user_data.get('waiting_for') == 'emotions':
            logger.info("============ PROCESSING EMOTIONS ============")
            logger.info(f"Received emotions text: {text}")
            logger.info(f"Current user data: {context.user_data}")

            try:
                # First send confirmation
                update.message.reply_text("✅ Получил ваши эмоции")
                logger.info("Sent confirmation message")

                # Save emotions
                context.user_data['emotions'] = text
                logger.info(f"Saved emotions: {text}")

                # Send transition message
                transition_message = (
                    "📝 Отлично! Теперь пришлите примеры постов, которые вам нравятся.\n\n"
                    "После каждого поста вы сможете:\n"
                    "• Добавить еще один пример\n"
                    "• Завершить добавление примеров\n\n"
                    "Пришлите первый пример:"
                )
                update.message.reply_text(transition_message)
                logger.info("Sent transition message")

                # Update state
                context.user_data['waiting_for'] = 'examples'
                context.user_data['examples'] = []
                logger.info("Updated state to examples")

                return EXAMPLES

            except Exception as e:
                logger.error("============ ERROR IN EMOTIONS HANDLER ============")
                logger.error(f"Error details: {str(e)}")
                logger.error(f"Current state: {context.user_data.get('waiting_for')}")
                logger.error(f"User data: {context.user_data}")
                logger.error("Stack trace:", exc_info=True)
                logger.error("===============================================")

                try:
                    update.message.reply_text(
                        "❌ Произошла ошибка. Пожалуйста, введите эмоции еще раз:"
                    )
                    return EMOTIONS
                except:
                    logger.error("Failed to send error message", exc_info=True)
                    return ConversationHandler.END

        elif context.user_data.get('waiting_for') == 'post_number':
            try:
                logger.info("============ PROCESSING POST NUMBER ============")
                logger.info(f"Received text: {text}")
                logger.info(f"Current user data: {context.user_data}")

                post_number = int(text)
                if 1 <= post_number <= 14:
                    update.message.reply_text(f"🔄 Получено число {post_number}, генерирую пост...")
                    user_data = get_user_data(update.effective_chat.id)

                    logger.info(f"Retrieved user data from database: {list(user_data.keys())}")

                    if not user_data or 'content_plan' not in user_data:
                        logger.error("Content plan not found in user data")
                        update.message.reply_text(
                            "❌ Ошибка: контент-план не найден. Пожалуйста, начните заново с команды /start"
                        )
                        return ConversationHandler.END

                    try:
                        generated_post = generate_post(user_data, post_number)
                        logger.info(f"Successfully generated post #{post_number}")

                        update.message.reply_text(
                            f"✨ Готово! Вот ваш пост #{post_number}:\n\n{generated_post}\n\n"
                            "Чтобы сгенерировать другой пост, введите его номер (1-14):",
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton("🔄 Сгенерировать новый контент-план", 
                                                   callback_data='new_plan')
                            ]])
                        )
                        return POST_NUMBER
                    except Exception as e:
                        logger.error(f"Error generating post: {e}", exc_info=True)
                        update.message.reply_text(
                            "❌ Произошла ошибка при генерации поста. Пожалуйста, попробуйте еще раз."
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
                logger.error(f"Unexpected error in post number handler: {e}", exc_info=True)
                update.message.reply_text(
                    "❌ Произошла неожиданная ошибка. Пожалуйста, начните заново с команды /start"
                )
                return ConversationHandler.END

        elif context.user_data.get('waiting_for') == 'repackage_audience':
            return handle_repackage_audience(update, context)
        elif context.user_data.get('waiting_for') == 'repackage_tool':
            return handle_repackage_tool(update, context)
        elif context.user_data.get('waiting_for') == 'repackage_result':
            return handle_repackage_result(update, context)

        logger.warning(f"Unexpected waiting_for state: {context.user_data.get('waiting_for')}")
        return ConversationHandler.END

    except Exception as e:
        logger.error("========== ERROR IN TEXT HANDLER ==========")
        logger.error(f"Error details: {str(e)}")
        logger.error(f"Current state: {context.user_data.get('waiting_for')}")
        logger.error(f"Available user data keys: {list(context.user_data.keys())}")
        logger.error("Full error details:", exc_info=True)
        logger.error("=========================================")

        update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
        )
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    update.message.reply_text('Операция отменена. Для начала напишите /start')
    return ConversationHandler.END