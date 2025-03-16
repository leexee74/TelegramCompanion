import os
from typing import Dict, Any
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_content_plan(user_data: Dict[str, Any]) -> str:
    """Generate a 14-day content plan using GPT-4."""
    try:
        prompt = f"""
        Создайте контент-план на 14 дней для Telegram канала. Учтите следующие детали:
        - Тема канала: {user_data.get('topic', '')}
        - Целевая аудитория: {user_data.get('audience', '')}
        - Дополнительные пожелания: {user_data.get('preferences', '')}
        - Желаемые эмоции аудитории: {user_data.get('emotions', '')}
        - Стиль написания: {user_data.get('style', '')}
        - Метод монетизации: {user_data.get('monetization', '')}
        - Детали продукта/услуги/курса: {user_data.get('product_details', '')}
        - Примеры постов: {user_data.get('examples', '')}

        Создайте 14 постов, по одному на каждый день. Для каждого поста укажите:
        1. 🎯 Цель поста: [engagement/продажи/информирование]
        2. 📢 Заголовок: [интригующий, кликбейтный заголовок]
        3. 📝 Описание: [краткое описание темы поста в одном предложении]

        Используйте эмодзи и форматирование для лучшей читаемости.
        Каждый пост должен быть отделен пустой строкой.
        Ответ должен быть на русском языке.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating content plan: {e}")
        raise

def generate_post(user_data: Dict[str, Any], post_number: int = None) -> str:
    """Generate a single post using GPT-4."""
    try:
        content_plan = user_data.get('content_plan', '')
        posts = content_plan.split('\n\n')
        selected_post = posts[post_number - 1] if post_number and post_number <= len(posts) else ""

        prompt = f"""
        Создайте пост для Telegram канала на основе следующей информации:
        - Тема канала: {user_data.get('topic', '')}
        - Целевая аудитория: {user_data.get('audience', '')}
        - Дополнительные пожелания: {user_data.get('preferences', '')}
        - Желаемые эмоции аудитории: {user_data.get('emotions', '')}
        - Стиль написания: {user_data.get('style', '')}
        - Метод монетизации: {user_data.get('monetization', '')}
        - Детали продукта/услуги/курса: {user_data.get('product_details', '')}

        Детали поста из контент-плана:
        {selected_post}

        Требования к посту:
        - Должен быть вовлекающим и естественным
        - Использовать реальные примеры, истории и кейсы
        - Умеренное использование эмодзи
        - Выделение ключевых моментов жирным шрифтом
        - Если монетизация через продукт/услугу, пост должен плавно подводить к покупке

        Ответ должен быть на русском языке.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating post: {e}")
        raise