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

        Каждый пункт контент-плана должен включать:
        1. Номер поста
        2. Интригующий заголовок в стиле кликбейт
        3. Краткое описание (1 предложение)
        4. Цель поста (вовлечение, продажи и т.д.)

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

def generate_post(user_data: Dict[str, Any]) -> str:
    """Generate a single post using GPT-4."""
    try:
        prompt = f"""
        Создайте пост для Telegram канала на основе следующей информации:
        - Тема канала: {user_data.get('topic', '')}
        - Целевая аудитория: {user_data.get('audience', '')}
        - Дополнительные пожелания: {user_data.get('preferences', '')}
        - Желаемые эмоции аудитории: {user_data.get('emotions', '')}
        - Стиль написания: {user_data.get('style', '')}
        - Метод монетизации: {user_data.get('monetization', '')}
        - Детали продукта/услуги/курса: {user_data.get('product_details', '')}

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
