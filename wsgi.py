from app import app
from main import run_telegram_bot
import threading

# Start Telegram bot in a separate thread when running in production
if __name__ != "__main__":  # This ensures bot only starts when running via gunicorn
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True  # Thread will be terminated when main process exits
    bot_thread.start()
