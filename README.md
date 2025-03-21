# GPT-4 Telegram Bot for Russian Social Media Content

A sophisticated Telegram bot leveraging GPT-4 to generate dynamic Russian-language social media content with intelligent post creation and adaptive user interaction capabilities.

## Features

- Dynamic content generation using GPT-4
- Russian language interface
- Content plan generation
- Post customization based on user preferences
- Interactive conversation flow
- Monetization strategy integration

## Technology Stack

- Python 3.11+
- python-telegram-bot
- OpenAI GPT-4
- Flask for web interface
- PostgreSQL for data storage
- Gunicorn for deployment

## Environment Variables Required

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
SESSION_SECRET=your_session_secret
DATABASE_URL=your_database_url
```

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables
4. Run the application:
   ```bash
   gunicorn --bind 0.0.0.0:5000 wsgi:app
   ```

## Project Structure

```
├── app.py              # Flask application setup
├── database.py         # Database operations
├── handlers.py         # Telegram message handlers
├── main.py            # Telegram bot initialization
├── prompts.py         # GPT-4 prompt templates
├── utils.py           # Utility functions
├── wsgi.py            # WSGI entry point
└── templates/         # HTML templates
    └── index.html     # Status page
```

## License

MIT License
