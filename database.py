import sqlite3
import json
import logging
from typing import Dict, Any, Optional

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
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

def save_user_data(chat_id: int, data: Dict[str, Any]) -> None:
    """Save user data to the database."""
    conn = None
    try:
        conn = sqlite3.connect('bot.db')
        c = conn.cursor()

        # Convert content_plan to JSON string if it exists
        if 'content_plan' in data:
            data['content_plan'] = json.dumps(data['content_plan'])

        c.execute('''
            INSERT OR REPLACE INTO users (
                chat_id, channel_topic, target_audience, monetization,
                product_details, preferences, style, emotions, examples, content_plan
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            data.get('content_plan', '')
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
    finally:
        if conn:
            conn.close()

def get_user_data(chat_id: int) -> Dict[str, Any]:
    """Retrieve user data from the database."""
    conn = None
    try:
        conn = sqlite3.connect('bot.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        row = c.fetchone()

        if row:
            # Convert row to dictionary
            columns = ['chat_id', 'channel_topic', 'target_audience', 'monetization',
                      'product_details', 'preferences', 'style', 'emotions', 'examples',
                      'content_plan']
            data = dict(zip(columns, row))

            # Parse content_plan JSON if it exists
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