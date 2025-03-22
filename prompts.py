import os
import logging
from openai import OpenAI
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Initialize OpenAI client
# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_product_repackaging(data: Dict[str, str]) -> str:
    """Generate product repackaging content using GPT-4."""
    try:
        logger.info("Generating product repackaging content...")
        logger.debug(f"Input data: {data}")

        prompt = f"""
        Создай переупаковку продукта на основе следующей информации:

        Целевая аудитория: {data.get('audience', '')}
        Инструмент/продукт: {data.get('tool', '')}
        Желаемый результат: {data.get('result', '')}

        Требования к структуре ответа:
        1. СНАЧАЛА сформулируй основную ценность в виде яркого маркетингового заголовка (одно предложение)
        2. Затем раздели текст на следующие блоки:

        ### Основная боль аудитории
        [Опиши основную проблему]

        ### Как продукт решает эту проблему
        [Объясни решение]

        ### Уникальность предложения
        [Подчеркни уникальные преимущества]

        ### Конкретный результат
        [Опиши измеримый результат]

        ### Призыв к действию
        [Добавь мотивирующий призыв]

        Требования к оформлению:
        - На русском языке
        - Структурированный текст
        - С эмодзи для лучшей читаемости
        - Убедительный, но без агрессивного маркетинга
        - Каждый блок должен начинаться с соответствующего заголовка и эмодзи
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        logger.info("Successfully generated product repackaging content")
        return content

    except Exception as e:
        logger.error(f"Error generating product repackaging: {e}", exc_info=True)
        return "❌ Извините, произошла ошибка при генерации контента. Пожалуйста, попробуйте позже или обратитесь в поддержку."

def generate_content_plan(user_data: Dict[str, Any], user_prefs: Dict[str, str] = None) -> str:
    """Generate a 14-day content plan using GPT-4."""
    try:
        # Combine user input with stored preferences
        if user_prefs:
            user_data['tone_of_voice'] = user_prefs.get('tone_of_voice', user_data.get('style', ''))
            user_data['content_theme'] = user_prefs.get('content_theme', user_data.get('topic', ''))

        prompt = f"""
        Создай контент-план на 14 дней для Telegram канала, строго учитывая следующие детали:
        - Тема канала: {user_data.get('content_theme', user_data.get('topic', ''))}
        - Целевая аудитория: {user_data.get('audience', '')}
        - Дополнительные пожелания: {user_data.get('preferences', '')}
        - Желаемые эмоции аудитории: {user_data.get('emotions', '')}
        - Стиль написания: {user_data.get('tone_of_voice', user_data.get('style', ''))}
        - Метод монетизации: {user_data.get('monetization', '')}
        - Детали продукта/услуги/курса: {user_data.get('product_details', '')}

        ВАЖНО: Структура прогрева аудитории:
        - Дни 1-5: Рассказ о проблемах и болях аудитории
        - Дни 6-9: Обсуждение возможных решений
        - Дни 10-11: Ваш экспертный опыт
        - Дни 12-14: Мягкое представление продукта

        Создай РОВНО 14 постов, пронумерованных от 1 до 14.
        Для каждого поста ОБЯЗАТЕЛЬНО укажи:
        1. 🔢 День #[номер]
        2. 🎯 Цель: [engagement/продажи/информирование]
        3. 📢 Заголовок: [интригующий заголовок]
        4. 📝 Описание: [краткое описание в одном предложении]
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error generating content plan: {e}")
        raise

def generate_post(user_data: Dict[str, Any], post_number: int, 
                 user_prefs: Dict[str, str] = None) -> str:
    """Generate a single post using GPT-4."""
    try:
        # Combine user input with stored preferences
        if user_prefs:
            user_data['tone_of_voice'] = user_prefs.get('tone_of_voice', user_data.get('style', ''))
            user_data['content_theme'] = user_prefs.get('content_theme', user_data.get('topic', ''))

        content_plan = user_data.get('content_plan', '')
        if not content_plan:
            raise ValueError("Content plan not found")

        prompt = f"""
        Создай пост для Telegram канала на основе следующей информации:
        - Тема канала: {user_data.get('content_theme', user_data.get('topic', ''))}
        - Целевая аудитория: {user_data.get('audience', '')}
        - Стиль написания: {user_data.get('tone_of_voice', user_data.get('style', ''))}
        - День #{post_number} из контент-плана

        Требования к посту:
        - Вовлекающий и естественный стиль
        - Использование реальных примеров
        - Умеренное использование эмодзи
        - Соответствие этапу прогрева (дни 1-5: проблемы, 6-9: решения, 
          10-11: экспертность, 12-14: продукт)
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error generating post: {e}")
        raise