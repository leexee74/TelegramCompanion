#!/bin/bash

# Kill any existing python processes
pkill -f "python server.py"
pkill -f "python main.py"
pkill -f "gunicorn"

# Start the application with gunicorn
exec gunicorn --bind 0.0.0.0:5000 \
    --worker-class=sync \
    --workers=1 \
    --timeout 120 \
    --reload \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
