import logging
from datetime import datetime
import json
from sqlalchemy import text
from app import db

logger = logging.getLogger(__name__)

def init_db():
    """Initialize the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect('bot.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                channel_topic TEXT,
                target_audience TEXT,
                monetization TEXT,
                product_details TEXT,
                preferences TEXT,
                style TEXT,
                emotions TEXT,
                examples TEXT,
                content_plan TEXT
            )
        ''')
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()


def save_user_preferences(chat_id: int, preferences: dict) -> None:
    """Save user preferences to the database."""
    try:
        query = text("""
            INSERT INTO user_data (chat_id, tone_of_voice, audience, content_theme, joined_at)
            VALUES (:chat_id, :tone_of_voice, :audience, :content_theme, :joined_at)
            ON CONFLICT (chat_id) 
            DO UPDATE SET 
                tone_of_voice = :tone_of_voice,
                audience = :audience,
                content_theme = :content_theme
        """)

        db.session.execute(query, {
            'chat_id': chat_id,
            'tone_of_voice': preferences.get('tone_of_voice', ''),
            'audience': preferences.get('audience', ''),
            'content_theme': preferences.get('content_theme', ''),
            'joined_at': datetime.utcnow()
        })
        db.session.commit()
        logger.info(f"Saved preferences for user {chat_id}")
    except Exception as e:
        logger.error(f"Error saving user preferences: {e}")
        db.session.rollback()
        raise

def get_user_preferences(chat_id: int) -> dict:
    """Retrieve user preferences from the database."""
    try:
        query = text("""
            SELECT tone_of_voice, audience, content_theme
            FROM user_data
            WHERE chat_id = :chat_id
        """)
        result = db.session.execute(query, {'chat_id': chat_id}).fetchone()

        if result:
            return {
                'tone_of_voice': result[0],
                'audience': result[1],
                'content_theme': result[2]
            }
        return {}
    except Exception as e:
        logger.error(f"Error retrieving user preferences: {e}")
        return {}

def save_scheduled_message(step_order: int, message_type: str, content: str, 
                         media_url: str = None, delay_minutes: int = 0) -> int:
    """Save a scheduled message to the database."""
    try:
        query = text("""
            INSERT INTO scheduled_messages 
            (step_order, message_type, content, media_url, delay_minutes)
            VALUES (:step_order, :message_type, :content, :media_url, :delay_minutes)
            RETURNING id
        """)

        result = db.session.execute(query, {
            'step_order': step_order,
            'message_type': message_type,
            'content': content,
            'media_url': media_url,
            'delay_minutes': delay_minutes
        })
        db.session.commit()
        message_id = result.fetchone()[0]
        logger.info(f"Saved scheduled message with ID {message_id}")
        return message_id
    except Exception as e:
        logger.error(f"Error saving scheduled message: {e}")
        db.session.rollback()
        raise

def get_scheduled_messages() -> list:
    """Retrieve all scheduled messages ordered by step_order."""
    try:
        query = text("""
            SELECT id, step_order, message_type, content, media_url, delay_minutes
            FROM scheduled_messages
            ORDER BY step_order
        """)
        result = db.session.execute(query)
        messages = []
        for row in result:
            messages.append({
                'id': row[0],
                'step_order': row[1],
                'message_type': row[2],
                'content': row[3],
                'media_url': row[4],
                'delay_minutes': row[5]
            })
        return messages
    except Exception as e:
        logger.error(f"Error retrieving scheduled messages: {e}")
        return []

def save_user_data(chat_id: int, data: dict) -> None:
    """Save user data to the database."""
    try:
        # Convert lists and dicts to JSON strings
        data_to_save = data.copy()
        if 'examples' in data_to_save and isinstance(data_to_save['examples'], list):
            data_to_save['examples'] = json.dumps(data_to_save['examples'])
        if 'content_plan' in data_to_save:
            data_to_save['content_plan'] = json.dumps(data_to_save['content_plan'])

        query = text("""
            INSERT INTO users (
                chat_id, channel_topic, target_audience, monetization,
                product_details, preferences, style, emotions, examples, content_plan
            ) VALUES (
                :chat_id, :topic, :audience, :monetization,
                :product_details, :preferences, :style, :emotions, :examples, :content_plan
            )
            ON CONFLICT (chat_id) DO UPDATE SET
                channel_topic = EXCLUDED.channel_topic,
                target_audience = EXCLUDED.target_audience,
                monetization = EXCLUDED.monetization,
                product_details = EXCLUDED.product_details,
                preferences = EXCLUDED.preferences,
                style = EXCLUDED.style,
                emotions = EXCLUDED.emotions,
                examples = EXCLUDED.examples,
                content_plan = EXCLUDED.content_plan
        """)

        db.session.execute(query, {
            'chat_id': chat_id,
            'topic': data_to_save.get('topic', ''),
            'audience': data_to_save.get('audience', ''),
            'monetization': data_to_save.get('monetization', ''),
            'product_details': data_to_save.get('product_details', ''),
            'preferences': data_to_save.get('preferences', ''),
            'style': data_to_save.get('style', ''),
            'emotions': data_to_save.get('emotions', ''),
            'examples': data_to_save.get('examples', ''),
            'content_plan': data_to_save.get('content_plan', '')
        })
        db.session.commit()
        logger.info(f"Saved data for user {chat_id}")
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
        db.session.rollback()
        raise

def get_user_data(chat_id: int) -> dict:
    """Retrieve user data from the database."""
    try:
        query = text("""
            SELECT 
                chat_id, channel_topic, target_audience, monetization,
                product_details, preferences, style, emotions, examples, content_plan
            FROM users
            WHERE chat_id = :chat_id
        """)
        result = db.session.execute(query, {'chat_id': chat_id}).fetchone()

        if result:
            data = {
                'chat_id': result[0],
                'topic': result[1],
                'audience': result[2],
                'monetization': result[3],
                'product_details': result[4],
                'preferences': result[5],
                'style': result[6],
                'emotions': result[7],
                'examples': result[8],
                'content_plan': result[9]
            }

            # Parse JSON strings back to Python objects
            if data['examples']:
                try:
                    data['examples'] = json.loads(data['examples'])
                except json.JSONDecodeError:
                    data['examples'] = []

            if data['content_plan']:
                try:
                    data['content_plan'] = json.loads(data['content_plan'])
                except json.JSONDecodeError:
                    data['content_plan'] = None

            return data
        return {}
    except Exception as e:
        logger.error(f"Error retrieving user data: {e}")
        return {}