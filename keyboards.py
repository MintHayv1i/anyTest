from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard():
    keyboard = [
        [KeyboardButton(text="💰 Курсы"), KeyboardButton(text="💱 Конвертер")],
        [KeyboardButton(text="📈 Топ"), KeyboardButton(text="🚀 Рост")],
        [KeyboardButton(text="📉 Падение"), KeyboardButton(text="ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_crypto_keyboard():
    from config import CRYPTO_CURRENCIES

    keyboard = []
    row = []

    for crypto in CRYPTO_CURRENCIES:
        row.append(InlineKeyboardButton(text=crypto.upper(), callback_data=f"price_{crypto}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_currency_type_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="💰 Криптовалюта", callback_data="convert_type_crypto")],
        [InlineKeyboardButton(text="💵 Фиатная валюта", callback_data="convert_type_fiat")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="convert_cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_crypto_currency_keyboard(currency_type: str, direction: str):
    from config import CONVERT_CURRENCIES

    currencies = CONVERT_CURRENCIES.get(currency_type, {})
    keyboard = []

    row = []
    for ticker, name in currencies.items():
        if direction == "from":
            callback_data = f"convert_from_{ticker}"
        else:
            callback_data = f"convert_to_{ticker}"

        row.append(InlineKeyboardButton(text=name, callback_data=callback_data))
        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="convert_back_type")])
    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data="convert_cancel")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="❌ Отмена", callback_data="convert_cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_top_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="Топ-5", callback_data="top_5"),
            InlineKeyboardButton(text="Топ-10", callback_data="top_10")
        ],
        [
            InlineKeyboardButton(text="Топ-20", callback_data="top_20"),
            InlineKeyboardButton(text="Топ-50", callback_data="top_50")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_chart_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="1 день", callback_data="chart_1"),
            InlineKeyboardButton(text="7 дней", callback_data="chart_7")
        ],
        [
            InlineKeyboardButton(text="30 дней", callback_data="chart_30"),
            InlineKeyboardButton(text="90 дней", callback_data="chart_90")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)