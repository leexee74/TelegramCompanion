from app import app
import threading
from main import run_telegram_bot

if __name__ == "__main__":
    # Start Telegram bot in a separate thread
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
