import logging
import os
import sys
import time
import fcntl
import signal
import atexit
import subprocess
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    CallbackQueryHandler, ConversationHandler
)
from handlers import (
    start, button_handler, handle_main_menu, cancel,
    handle_repackage_audience, handle_repackage_tool, handle_repackage_result,
    handle_content_topic, handle_content_audience, handle_content_monetization,
    handle_content_product,
    SUBSCRIPTION_CHECK, MAIN_MENU, REPACKAGE_AUDIENCE, REPACKAGE_TOOL, REPACKAGE_RESULT,
    CONTENT_TOPIC, CONTENT_AUDIENCE, CONTENT_MONETIZATION, CONTENT_PRODUCT
)
# Removed import to fix circular dependency

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('telegram_bot.log')
    ]
)
logger = logging.getLogger(__name__)

def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.error(f"============ ERROR OCCURRED ============")
    logger.error(f"Update: {update}")
    logger.error(f"Error: {context.error}")
    logger.error("========================================", exc_info=True)

_updater = None

def run_telegram_bot():
    """Start the bot."""
    global _updater
    try:
        # Initialize the bot
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            logger.error("Telegram bot token not found!")
            return

        # Clear any existing updater
        if _updater:
            logger.info("Stopping existing bot instance...")
            _updater.stop()
            _updater = None

        logger.info("Starting new bot instance...")

        # Create the Updater and pass it your bot's token
        _updater = Updater(token=TOKEN, use_context=True)
        dispatcher = _updater.dispatcher
        logger.info("Bot dispatcher initialized")

        # Add error handler
        dispatcher.add_error_handler(error_handler)
        logger.info("Error handler added")

        # Create conversation handler with states
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                SUBSCRIPTION_CHECK: [
                    CallbackQueryHandler(button_handler, pattern='^check_subscription$')
                ],
                MAIN_MENU: [
                    CallbackQueryHandler(handle_main_menu)
                ],
                CONTENT_TOPIC: [
                    MessageHandler(Filters.text & ~Filters.command, handle_content_topic),
                    CallbackQueryHandler(handle_main_menu, pattern='^back_to_menu$')
                ],
                CONTENT_AUDIENCE: [
                    MessageHandler(Filters.text & ~Filters.command, handle_content_audience),
                    CallbackQueryHandler(handle_main_menu, pattern='^back_to_menu$')
                ],
                CONTENT_MONETIZATION: [
                    MessageHandler(Filters.text & ~Filters.command, handle_content_monetization),
                    CallbackQueryHandler(handle_main_menu, pattern='^back_to_menu$')
                ],
                CONTENT_PRODUCT: [
                    MessageHandler(Filters.text & ~Filters.command, handle_content_product),
                    CallbackQueryHandler(handle_main_menu, pattern='^back_to_menu$')
                ],
                REPACKAGE_AUDIENCE: [
                    MessageHandler(Filters.text & ~Filters.command, handle_repackage_audience),
                    CallbackQueryHandler(handle_main_menu, pattern='^back_to_menu$')
                ],
                REPACKAGE_TOOL: [
                    MessageHandler(Filters.text & ~Filters.command, handle_repackage_tool),
                    CallbackQueryHandler(handle_main_menu, pattern='^back_to_menu$')
                ],
                REPACKAGE_RESULT: [
                    MessageHandler(Filters.text & ~Filters.command, handle_repackage_result),
                    CallbackQueryHandler(handle_main_menu, pattern='^back_to_menu$')
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            allow_reentry=True
        )

        # Add handler to dispatcher
        dispatcher.add_handler(conv_handler)
        logger.info("Conversation handler added")

        # Start the Bot with error handling for conflicts
        def start_polling():
            try:
                logger.info("Bot starting...")
                _updater.start_polling(drop_pending_updates=True)
                logger.info("Bot started successfully!")
            except Exception as e:
                if "Conflict: terminated by other getUpdates request" in str(e):
                    logger.warning("Conflict detected with another bot instance. Retrying in 5 seconds...")
                    time.sleep(5)
                    start_polling()
                else:
                    logger.error(f"Failed to start bot: {e}", exc_info=True)
                    raise

        start_polling()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

# Функция для очистки работающих процессов и ресурсов при завершении
def cleanup_resources():
    global _updater
    if _updater:
        logger.info("Shutting down bot updater...")
        try:
            _updater.stop()
            _updater = None
        except Exception as e:
            logger.error(f"Error stopping updater: {e}")

    # Освобождаем файл блокировки
    if 'lock_file' in globals():
        try:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()
            logger.info("Lock file released")
        except Exception as e:
            logger.error(f"Error releasing lock file: {e}")

# Обработчик сигналов для корректного завершения работы
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down...")
    cleanup_resources()
    sys.exit(0)

# Проверка на уже запущенные экземпляры бота и их завершение
def kill_other_instances():
    try:
        # Получаем PID текущего процесса
        current_pid = os.getpid()
        
        # Находим все процессы Python, запускающие main.py
        cmd = "ps aux | grep 'python.*main.py' | grep -v grep | awk '{print $2}'"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, _ = process.communicate()
        
        # Преобразуем вывод в список PID
        pids = [int(pid) for pid in output.decode().strip().split("\n") if pid]
        
        # Завершаем все процессы, кроме текущего
        for pid in pids:
            if pid != current_pid:
                logger.info(f"Killing existing bot process with PID {pid}")
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)  # Даем процессу время на корректное завершение
                except ProcessLookupError:
                    pass  # Процесс уже завершен
                except Exception as e:
                    logger.error(f"Error killing process {pid}: {e}")
        
        # Удаляем старый файл блокировки, если он существует
        if os.path.exists("telegram_bot.lock"):
            try:
                os.remove("telegram_bot.lock")
                logger.info("Removed stale lock file")
            except:
                pass
                
        return True
    except Exception as e:
        logger.error(f"Error checking for other instances: {e}")
        return False

if __name__ == '__main__':
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup_resources)
    
    # Завершаем другие экземпляры бота
    kill_other_instances()
    
    # Создаем новый файл блокировки
    lock_file = open("telegram_bot.lock", "w")
    try:
        # Пытаемся получить эксклюзивную блокировку
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        logger.info("Starting bot application...")
        run_telegram_bot()
    except IOError:
        logger.error("Another instance of the bot is already running!")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error in main: {e}", exc_info=True)
        sys.exit(1)