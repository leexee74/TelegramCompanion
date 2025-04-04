import sqlite3
import json
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Initialize the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect('bot.db')
        c = conn.cursor()

        # Create users table with extended fields
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
                content_plan TEXT,
                tone_of_voice TEXT,
                saved_audience TEXT,
                content_theme TEXT,
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

def save_user_preferences(chat_id: int, data: dict) -> None:
    """Save user preferences to the database."""
    conn = None
    try:
        conn = sqlite3.connect('bot.db')
        c = conn.cursor()

        c.execute('''
            UPDATE users SET 
                tone_of_voice = ?,
                saved_audience = ?,
                content_theme = ?,
                last_interaction = CURRENT_TIMESTAMP
            WHERE chat_id = ?
        ''', (
            data.get('tone_of_voice', ''),
            data.get('saved_audience', ''),
            data.get('content_theme', ''),
            chat_id
        ))

        if c.rowcount == 0:  # No existing record, insert new one
            c.execute('''
                INSERT INTO users (
                    chat_id, tone_of_voice, saved_audience, content_theme
                ) VALUES (?, ?, ?, ?)
            ''', (
                chat_id,
                data.get('tone_of_voice', ''),
                data.get('saved_audience', ''),
                data.get('content_theme', '')
            ))

        conn.commit()
        logger.info(f"Saved preferences for user {chat_id}")
    except Exception as e:
        logger.error(f"Error saving user preferences: {e}")
    finally:
        if conn:
            conn.close()

def save_user_data(chat_id: int, data: dict) -> None:
    """Save user data to the database."""
    conn = None
    try:
        conn = sqlite3.connect('bot.db')
        c = conn.cursor()

        # Convert lists and dicts to JSON strings
        if 'examples' in data and isinstance(data['examples'], list):
            data['examples'] = json.dumps(data['examples'])
        if 'content_plan' in data:
            data['content_plan'] = json.dumps(data['content_plan'])

        c.execute('''
            INSERT OR REPLACE INTO users (
                chat_id, channel_topic, target_audience, monetization,
                product_details, preferences, style, emotions, examples, content_plan,
                tone_of_voice, saved_audience, content_theme
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            chat_id,
            data.get('topic', ''),
            data.get('audience', ''),
            data.get('monetization', ''),
            data.get('product_details', ''),
            data.get('preferences', ''),
            data.get('style', ''),
            data.get('emotions', ''),
            data.get('examples', ''),
            data.get('content_plan', ''),
            data.get('tone_of_voice', ''),
            data.get('saved_audience', ''),
            data.get('content_theme', '')
        ))
        conn.commit()
        logger.info(f"Saved data for user {chat_id}")
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
    finally:
        if conn:
            conn.close()

def get_user_data(chat_id: int) -> dict:
    """Retrieve user data from the database."""
    conn = None
    try:
        conn = sqlite3.connect('bot.db')
        c = conn.cursor()
        c.execute('''
            SELECT 
                chat_id, channel_topic, target_audience, monetization,
                product_details, preferences, style, emotions, examples,
                content_plan, tone_of_voice, saved_audience, content_theme
            FROM users 
            WHERE chat_id = ?
        ''', (chat_id,))
        row = c.fetchone()

        if row:
            columns = [
                'chat_id', 'channel_topic', 'target_audience', 'monetization',
                'product_details', 'preferences', 'style', 'emotions', 'examples',
                'content_plan', 'tone_of_voice', 'saved_audience', 'content_theme'
            ]
            data = dict(zip(columns, row))

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
    finally:
        if conn:
            conn.close()