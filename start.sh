#!/bin/bash

# Kill any existing python processes
pkill -f "python server.py" || true
pkill -f "python main.py" || true
pkill -f "gunicorn" || true

# Wait for processes to terminate
sleep 2

# Clear existing log files
> telegram_bot.log

# Start the bot directly
exec python main.py
