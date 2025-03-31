#!/bin/bash

echo "Запуск веб-сервера Flask..."
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload wsgi:app