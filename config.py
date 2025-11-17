import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Токен бота не найден! Проверь файл .env")

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

POPULAR_CRYPTO = {
    'btc': 'bitcoin',
    'eth': 'ethereum',
    'sol': 'solana',
    'bnb': 'binancecoin',
    'xrp': 'ripple',
    'ada': 'cardano',
    'doge': 'dogecoin',
    'dot': 'polkadot',
    'matic': 'polygon-pos',
    'avax': 'avalanche-2'
}

REQUEST_DELAY = 3.0
MAX_REQUESTS_PER_MINUTE = 30

BOT_SETTINGS = {
    "parse_mode": "HTML",
    "disable_web_page_preview": True,
    "timeout": 30
}

BOT_MESSAGES = {
    "welcome": "🤖 Крипто-трекер запущен!\nВыбери опцию ниже:",
    "help": (
        "ℹ️ Использование:\n\n"
        "📊 Курсы - цены популярных монет\n"
        "🏆 Топ-5 - лидеры по капитализации\n"
        "🚀 Рост - самые растущие монеты\n"
        "💥 Падение - самые падающие монеты\n\n"
        "💡 Или просто напиши название монеты (bitcoin, ethereum...)\n\n"
        "📈 /graph bitcoin - показать график цены\n"
        "⚠️ Ограничение: 1 запрос в 3 секунды"
    ),
    "too_many_requests": "⏰ Слишком много запросов. Подожди 1-2 минуты.",
    "coin_not_found": "❌ Монета не найдена",
    "api_error": "❌ Ошибка API",
    "network_error": "❌ Ошибка сети",
    "api_timeout": "⏰ Таймаут запроса"
}

KEYBOARD_SETTINGS = {
    "crypto_buttons_per_row": 3,
    "resize_keyboard": True
}

API_SETTINGS = {
    "timeout": 15,
    "retry_attempts": 3,
    "cache_duration": 60
}

CURRENCIES = ['usd', 'rub']

NUMBER_FORMATTING = {
    "usd_decimals": 2,
    "rub_decimals": 0,
    "percentage_decimals": 2
}

EMOJIS = {
    "up": "📈", "down": "📉", "neutral": "➡️",
    "money": "💰", "trophy": "🏆", "rocket": "🚀",
    "fire": "💥", "error": "❌", "time": "⏰", "info": "ℹ️",
    "chart": "📊", "refresh": "🔄"
}

print("Конфигурация загружена успешно!")