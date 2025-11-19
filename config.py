import os
from dotenv import load_dotenv

load_dotenv()

# Токены
BOT_TOKEN = os.getenv('BOT_TOKEN')
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')

# API
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
REQUEST_DELAY = 1

# Валюты для отображения
CURRENCIES = ['usd', 'rub', 'eur', 'kzt', 'uah']

# Криптовалюты для быстрого доступа
CRYPTO_CURRENCIES = [
    'bitcoin', 'ethereum', 'solana', 'binancecoin', 'ripple',
    'cardano', 'dogecoin', 'polkadot', 'polygon-pos', 'avalanche-2'
]

# Валюты для конвертера
CONVERT_CURRENCIES = {
    'crypto': {
        'btc': 'Bitcoin',
        'eth': 'Ethereum',
        'sol': 'Solana',
        'bnb': 'Binance Coin',
        'xrp': 'Ripple',
        'ada': 'Cardano',
        'doge': 'Dogecoin',
        'dot': 'Polkadot',
        'matic': 'Polygon',
        'avax': 'Avalanche'
    },
    'fiat': {
        'usd': 'US Dollar',
        'rub': 'Russian Ruble',
        'eur': 'Euro',
        'kzt': 'Kazakhstani Tenge',
        'uah': 'Ukrainian Hryvnia'
    }
}

# Emoji
EMOJIS = {
    "up": "📈",
    "down": "📉",
    "neutral": "➡️",
    "money": "💰",
    "trophy": "🏆",
    "rocket": "🚀",
    "fire": "🔥"
}

# Сообщения бота
BOT_MESSAGES = {
    "start": "🤖 <b>Крипто-трекер бот</b>\n\nЯ помогу отслеживать курсы криптовалют и конвертировать валюты!\n\n💡 <b>Используйте кнопки ниже для быстрого доступа!</b>",
    "help": "ℹ️ <b>Помощь по боту</b>\n\n📊 <b>Функции:</b>\n• Курсы криптовалют в реальном времени\n• Конвертер между крипто и фиатными валютами\n• Топ криптовалют по капитализации\n• Графики цен\n• Свежие новости крипторынка\n\n💡 <b>Как использовать:</b>\n• Нажмите '💰 Курсы' для просмотра цен\n• '💱 Конвертер' для конвертации валют\n• '📈 Топ' для списка топовых монет\n• '🚀 Рост' и '📉 Падение' для лидеров роста/падения\n• '📰 Новости' для свежих новостей",
    "select_from_currency": "💱 <b>Конвертер валют</b>\n\n📥 Выберите тип исходной валюты:",
    "select_to_currency": "📤 Выберите тип целевой валюты:",
    "convert_same_currency": "❌ Нельзя конвертировать одинаковые валюты!",
    "convert_invalid_amount": "❌ Введите корректную сумму:",
    "convert_error": "❌ Ошибка конвертации. Попробуйте позже.",
    "too_many_requests": "⏳ Слишком много запросов...",
    "api_error": "❌ Ошибка API.",
    "coin_not_found": "❌ Криптовалюта не найдена."
}

print("Конфигурация загружена успешно!")