import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# API
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
REQUEST_DELAY = 1  # Задержка между запросами в секундах

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
    "fire": "🔥",
    "chart": "📊",
    "clock": "⏰"
}

# Сообщения бота
BOT_MESSAGES = {
    "start": "🤖 <b>Крипто-трекер бот</b>\n\n"
             "Я помогу отслеживать курсы криптовалют и конвертировать валюты!\n\n"
             "📊 <b>Доступные команды:</b>\n"
             "• /start - Главное меню\n"
             "• /help - Помощь\n"
             "• /convert - Конвертер валют\n"
             "• /top - Топ криптовалют\n\n"
             "💡 <b>Используйте кнопки ниже для быстрого доступа!</b>",

    "help": "ℹ️ <b>Помощь по боту</b>\n\n"
            "📊 <b>Функции:</b>\n"
            "• Курсы криптовалют в реальном времени\n"
            "• Конвертер между крипто и фиатными валютами\n"
            "• Топ криптовалют по капитализации\n"
            "• Графики цен\n\n"
            "💡 <b>Как использовать:</b>\n"
            "• Нажмите '💰 Курсы' для просмотра цен\n"
            "• '💱 Конвертер' для конвертации валют\n"
            "• '📈 Топ' для списка топовых монет\n"
            "• '🚀 Рост' и '📉 Падение' для лидеров роста/падения",

    "select_from_currency": "💱 <b>Конвертер валют</b>\n\n"
                            "📥 Выберите <b>тип исходной валюты</b>:",

    "select_to_currency": "📤 Теперь выберите <b>тип целевой валюты</b>:",

    "convert_same_currency": "❌ Нельзя конвертировать одинаковые валюты!",

    "convert_invalid_amount": "❌ Пожалуйста, введите корректную сумму (число больше 0):",

    "convert_error": "❌ Ошибка конвертации. Попробуйте позже.",

    "too_many_requests": "⏳ Слишком много запросов. Подождите немного...",

    "api_error": "❌ Ошибка API. Попробуйте позже.",

    "coin_not_found": "❌ Криптовалюта не найдена.",

    "wait_for_price": "⏳ Загружаю данные..."
}

print("Конфигурация загружена успешно!")