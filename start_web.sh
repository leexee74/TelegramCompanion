#!/bin/bash

# Kill any existing web server processes
pkill -f "gunicorn" || true
pkill -f "flask" || true

# Wait for processes to terminate
sleep 2

# Clear existing log files
> server.log
> wsgi.log

# Start the web application with gunicorn
exec gunicorn --bind 0.0.0.0:5000 \
    --worker-class=sync \
    --workers=1 \
    --timeout 120 \
    --reload \
    --access-logfile - \
    --error-logfile - \
    wsgi:app