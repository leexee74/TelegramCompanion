from app import app
from main import run_telegram_bot, stop_telegram_bot
import threading
import logging
import os
import atexit
import signal
import socket
import sys
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_bot_thread = None
_server_socket = None

def check_port_available(port):
    """Check if a port is available."""
    global _server_socket
    try:
        # Close existing socket if any
        if _server_socket:
            try:
                _server_socket.close()
            except:
                pass
            _server_socket = None
            # Give the system time to release the port
            time.sleep(1)

        _server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _server_socket.bind(('0.0.0.0', port))
        return True
    except socket.error as e:
        logger.error(f"Port {port} is not available: {e}")
        return False

def check_required_vars():
    """Check if all required environment variables are set."""
    required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SESSION_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

def start_bot():
    """Start the Telegram bot in a separate thread if not already running."""
    global _bot_thread
    if _bot_thread is None or not _bot_thread.is_alive():
        try:
            logger.info("Starting Telegram bot thread")
            _bot_thread = threading.Thread(target=run_telegram_bot)
            _bot_thread.daemon = True  # Make thread daemon so it exits when main thread exits
            _bot_thread.start()
            logger.info("Telegram bot thread started successfully")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot thread: {e}", exc_info=True)
            raise

def cleanup():
    """Cleanup function to be called on exit."""
    try:
        logger.info("Running cleanup...")
        # Stop the bot
        stop_telegram_bot()

        # Close server socket
        global _server_socket
        if _server_socket:
            try:
                _server_socket.close()
            except:
                pass
            _server_socket = None

        logger.info("Cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def signal_handler(signum, frame):
    """Handle termination signals."""
    logger.info(f"Received signal {signum}")
    cleanup()
    sys.exit(0)

# Register cleanup function
atexit.register(cleanup)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Handle Flask application
if __name__ == "__main__":
    # Running directly
    if check_required_vars():
        if check_port_available(5000):
            try:
                start_bot()
                # Release the socket for Flask
                if _server_socket:
                    _server_socket.close()
                    _server_socket = None
                app.run(host="0.0.0.0", port=5000)
            except Exception as e:
                logger.error(f"Failed to start application: {e}")
                cleanup()
                sys.exit(1)
        else:
            logger.error("Port 5000 is not available")
            sys.exit(1)
    else:
        logger.error("Cannot start server: missing required environment variables")
        sys.exit(1)
else:
    # Running under Gunicorn
    if check_required_vars():
        if check_port_available(5000):
            try:
                start_bot()
                # Release the socket for Gunicorn
                if _server_socket:
                    _server_socket.close()
                    _server_socket = None
                logger.info("Bot started successfully under Gunicorn")
            except Exception as e:
                logger.error(f"Failed to start bot under Gunicorn: {e}")
                cleanup()
                sys.exit(1)
        else:
            logger.error("Port 5000 is not available")
            sys.exit(1)
    else:
        logger.error("Cannot start server: missing required environment variables")
        sys.exit(1)