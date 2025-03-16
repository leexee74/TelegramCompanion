import os
import re
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
        Создай контент-план на 14 дней для Telegram канала, строго учитывая следующие детали:
        - Тема канала: {user_data.get('topic', '')}
        - Целевая аудитория: {user_data.get('audience', '')}
        - Дополнительные пожелания: {user_data.get('preferences', '')}
        - Желаемые эмоции аудитории: {user_data.get('emotions', '')}
        - Стиль написания: {user_data.get('style', '')}
        - Метод монетизации: {user_data.get('monetization', '')}
        - Детали продукта/услуги/курса: {user_data.get('product_details', '')}

        Создай РОВНО 14 постов, пронумерованных от 1 до 14 последовательно.
        Для каждого поста ОБЯЗАТЕЛЬНО укажи:
        1. 🔢 День #[номер]: (от 1 до 14)
        2. 🎯 Цель: [engagement/продажи/информирование]
        3. 📢 Заголовок: [интригующий, кликбейтный заголовок]
        4. 📝 Описание: [краткое описание темы поста в одном предложении]

        ВАЖНО:
        - Строго соблюдай последовательную нумерацию от 1 до 14
        - Каждый пост должен быть отделен пустой строкой
        - Используй эмодзи для лучшей читаемости
        - Ответ должен быть на русском языке
        - НЕ добавляй никакого вступительного или заключительного текста
        - НЕ пропускай номера постов
        - Начинай КАЖДЫЙ пост СТРОГО с "🔢 День #" и номера

        Пример формата для каждого поста:
        🔢 День #1:
        🎯 Цель: engagement
        📢 Заголовок: [кликбейтный заголовок]
        📝 Описание: [одно предложение]
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content_plan = response.choices[0].message.content.strip()

        # Verify the content plan format
        posts = re.findall(r'🔢 День #(\d+):[^\n]*(?:\n(?!🔢 День #)[^\n]*)*', content_plan, re.MULTILINE)
        post_numbers = [int(num) for num in posts]
        logger.info(f"Generated content plan. Found posts with numbers: {post_numbers}")

        if len(post_numbers) != 14 or sorted(post_numbers) != list(range(1, 15)):
            logger.error(f"Invalid content plan: Wrong number of posts or missing numbers. Found: {post_numbers}")
            raise ValueError("Generated content plan does not contain exactly 14 sequential posts")

        return content_plan

    except Exception as e:
        logger.error(f"Error generating content plan: {e}")
        raise

def generate_post(user_data: Dict[str, Any], post_number: int) -> str:
    """Generate a single post using GPT-4."""
    try:
        if not post_number or not (1 <= post_number <= 14):
            logger.error(f"Invalid post number: {post_number}")
            raise ValueError("Invalid post number")

        content_plan = user_data.get('content_plan', '')
        if not content_plan:
            logger.error("Content plan not found in user data")
            raise ValueError("Content plan not found")

        # Extract posts using regex
        logger.info(f"Extracting post #{post_number} from content plan")
        posts = re.findall(r'(🔢 День #(\d+):[^\n]*(?:\n(?!🔢 День #)[^\n]*)*)', content_plan, re.MULTILINE)
        logger.info(f"Found {len(posts)} posts in content plan")

        # Find the target post
        target_post = None
        for post_content, post_num in posts:
            if int(post_num) == post_number:
                target_post = post_content.strip()
                break

        if not target_post:
            logger.error(f"Post #{post_number} not found in content plan")
            logger.debug(f"Available posts: {[int(num) for _, num in posts]}")
            raise ValueError(f"Post #{post_number} not found in content plan")

        logger.info(f"Found post #{post_number} in content plan")

        prompt = f"""
        Создай полный пост для Telegram канала на основе следующей информации:
        - Тема канала: {user_data.get('topic', '')}
        - Целевая аудитория: {user_data.get('audience', '')}
        - Дополнительные пожелания: {user_data.get('preferences', '')}
        - Желаемые эмоции аудитории: {user_data.get('emotions', '')}
        - Стиль написания: {user_data.get('style', '')}
        - Метод монетизации: {user_data.get('monetization', '')}
        - Детали продукта/услуги/курса: {user_data.get('product_details', '')}

        Детали поста из контент-плана:
        {target_post}

        Требования к посту:
        - Пост должен полностью соответствовать указанной цели
        - Использовать заголовок и тему из контент-плана
        - Должен быть вовлекающим и естественным
        - Использовать реальные примеры, истории и кейсы
        - Умеренное использование эмодзи
        - Выделение ключевых моментов жирным шрифтом
        - Если монетизация через продукт/услугу, пост должен плавно подводить к покупке

        Ответ должен быть на русском языке.
        """

        logger.info("Sending request to OpenAI for post generation")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        post_content = response.choices[0].message.content.strip()
        logger.info(f"Successfully generated full post #{post_number}")
        return post_content

    except Exception as e:
        logger.error(f"Error generating post: {e}")
        raise