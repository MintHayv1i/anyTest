import asyncio
import time
import requests
import matplotlib.pyplot as plt
import io
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command

from config import (
    BOT_TOKEN, POPULAR_CRYPTO, COINGECKO_API_URL,
    REQUEST_DELAY, BOT_MESSAGES, EMOJIS,
    KEYBOARD_SETTINGS, CURRENCIES, NUMBER_FORMATTING
)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

price_cache = {}
cache_timeout = 60

MENU_COMMANDS = {
    "📊 Курсы", "Курсы",
    "🏆 Топ-5", "Топ-5",
    "🚀 Рост", "Рост",
    "💥 Падение", "Падение"
}

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Курсы"), KeyboardButton(text="🏆 Топ-5")],
            [KeyboardButton(text="🚀 Рост"), KeyboardButton(text="💥 Падение")]
        ],
        resize_keyboard=KEYBOARD_SETTINGS["resize_keyboard"]
    )

def get_crypto_keyboard():
    buttons = []
    for ticker in POPULAR_CRYPTO.keys():
        buttons.append(InlineKeyboardButton(
            text=ticker.upper(),
            callback_data=f"price_{ticker}"
        ))

    keyboard = []
    for i in range(0, len(buttons), KEYBOARD_SETTINGS["crypto_buttons_per_row"]):
        keyboard.append(buttons[i:i + KEYBOARD_SETTINGS["crypto_buttons_per_row"]])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_chart_keyboard(crypto_ticker: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 График 7д", callback_data=f"chart_{crypto_ticker}"),
            InlineKeyboardButton(text="📊 График 30д", callback_data=f"chart30_{crypto_ticker}")
        ],
        [
            InlineKeyboardButton(text="🔄 Обновить", callback_data=f"price_{crypto_ticker}")
        ]
    ])

def make_sync_api_request(url: str, params: dict):
    try:
        response = requests.get(url, params=params, timeout=15)
        return response
    except requests.exceptions.Timeout:
        raise Exception("Таймаут запроса")
    except requests.exceptions.ConnectionError:
        raise Exception("Ошибка подключения")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка запроса: {str(e)}")

async def generate_price_chart(crypto_id: str, days: int = 7):
    try:
        url = f"{COINGECKO_API_URL}/coins/{crypto_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }

        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            return None

        data = response.json()
        prices = data['prices']

        timestamps = [point[0] for point in prices]
        price_values = [point[1] for point in prices]

        dates = [datetime.fromtimestamp(ts / 1000) for ts in timestamps]

        plt.figure(figsize=(10, 6), facecolor='#1e1e1e')
        ax = plt.axes()
        ax.set_facecolor('#1e1e1e')

        first_price = price_values[0]
        last_price = price_values[-1]
        line_color = '#00ff00' if last_price >= first_price else '#ff0000'

        plt.plot(dates, price_values, color=line_color, linewidth=3, marker='o', markersize=3)

        plt.title(f'{crypto_id.upper()} Price Chart ({days} days)', color='white', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', color='white', fontsize=12)
        plt.ylabel('Price (USD)', color='white', fontsize=12)
        plt.grid(True, alpha=0.3, color='gray')

        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')

        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='#1e1e1e', edgecolor='none')
        buf.seek(0)
        plt.close()

        return buf

    except Exception as e:
        print(f"Ошибка генерации графика: {e}")
        return None

async def get_crypto_price(crypto_id: str):
    cache_key = f"price_{crypto_id}"
    if cache_key in price_cache:
        cache_data, cache_timestamp = price_cache[cache_key]
        if time.time() - cache_timestamp < cache_timeout:
            return cache_data

    url = f"{COINGECKO_API_URL}/simple/price"
    params = {
        'ids': crypto_id,
        'vs_currencies': ','.join(CURRENCIES),
        'include_24hr_change': 'true',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true'
    }

    try:
        await asyncio.sleep(REQUEST_DELAY)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, make_sync_api_request, url, params)

        if response.status_code == 429:
            result = BOT_MESSAGES["too_many_requests"]
        elif response.status_code != 200:
            result = f"❌ Ошибка API: статус {response.status_code}"
        else:
            data = response.json()

            if not isinstance(data, dict):
                result = BOT_MESSAGES["api_error"]
            elif crypto_id in data:
                crypto_data = data[crypto_id]

                if not isinstance(crypto_data, dict):
                    result = BOT_MESSAGES["api_error"]
                else:
                    change = crypto_data.get('usd_24h_change', 0)
                    change_emoji = EMOJIS["up"] if change > 0 else EMOJIS["down"] if change < 0 else EMOJIS["neutral"]

                    usd_price = crypto_data.get('usd', 0)
                    rub_price = crypto_data.get('rub', 0)
                    market_cap = crypto_data.get('usd_market_cap', 0)
                    volume_24h = crypto_data.get('usd_24h_vol', 0)

                    usd_formatted = f"{usd_price:,.2f}"
                    rub_formatted = f"{rub_price:,.0f}"
                    change_formatted = f"{change:+.2f}"
                    market_cap_formatted = f"{market_cap:,.0f}"
                    volume_formatted = f"{volume_24h:,.0f}"

                    def get_text_chart(change_val):
                        if change_val > 10:
                            return "🟢🟢🟢🟢🟢"
                        elif change_val > 5:
                            return "🟢🟢🟢🟢⚪"
                        elif change_val > 0:
                            return "🟢🟢🟢⚪⚪"
                        elif change_val > -5:
                            return "🔴🔴🔴⚪⚪"
                        elif change_val > -10:
                            return "🔴🔴🔴🔴⚪"
                        else:
                            return "🔴🔴🔴🔴🔴"

                    chart = get_text_chart(change)
                    update_time = datetime.now().strftime("%H:%M:%S")

                    result = (f"💰 {crypto_id.upper()}\n"
                              f"💵 ${usd_formatted} | ₽ {rub_formatted} руб\n\n"
                              f"📈 Изменение: {chart} {change_emoji} {change_formatted}% за 24ч\n\n"
                              f"📊 Капитализация: ${market_cap_formatted}\n"
                              f"💰 Объем 24ч: ${volume_formatted}\n\n"
                              f"🕐 Обновлено: {update_time}")
            else:
                result = BOT_MESSAGES["coin_not_found"]

        price_cache[cache_key] = (result, time.time())
        return result

    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        return error_msg

async def get_top_cryptos(limit: int = 5):
    cache_key = f"top_{limit}"
    if cache_key in price_cache:
        cache_data, cache_timestamp = price_cache[cache_key]
        if time.time() - cache_timestamp < cache_timeout:
            return cache_data

    url = f"{COINGECKO_API_URL}/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': limit
    }

    try:
        await asyncio.sleep(REQUEST_DELAY)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, make_sync_api_request, url, params)

        if response.status_code == 429:
            result = BOT_MESSAGES["too_many_requests"]
        elif response.status_code != 200:
            result = f"❌ Ошибка API: статус {response.status_code}"
        else:
            data = response.json()

            if not isinstance(data, list):
                result = BOT_MESSAGES["api_error"]
            else:
                result = f"{EMOJIS['trophy']} Топ-{limit} криптовалют:\n\n"
                for i, crypto in enumerate(data, 1):
                    if not isinstance(crypto, dict):
                        continue

                    change = crypto.get('price_change_percentage_24h', 0) or 0
                    change_emoji = EMOJIS["up"] if change > 0 else EMOJIS["down"] if change < 0 else EMOJIS["neutral"]

                    result += (f"{i}. {crypto.get('symbol', 'N/A').upper()} - {crypto.get('name', 'Unknown')}\n"
                               f"   {EMOJIS['money']} ${crypto.get('current_price', 0):,.2f}\n"
                               f"   {change_emoji} {change:+.2f}%\n\n")

        price_cache[cache_key] = (result, time.time())
        return result

    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

async def get_movers(is_gainers: bool = True):
    cache_key = f"movers_{'up' if is_gainers else 'down'}"
    if cache_key in price_cache:
        cache_data, cache_timestamp = price_cache[cache_key]
        if time.time() - cache_timestamp < cache_timeout:
            return cache_data

    url = f"{COINGECKO_API_URL}/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'volume_desc',
        'per_page': 15
    }

    try:
        await asyncio.sleep(REQUEST_DELAY)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, make_sync_api_request, url, params)

        if response.status_code == 429:
            result = BOT_MESSAGES["too_many_requests"]
        elif response.status_code != 200:
            result = f"❌ Ошибка API: статус {response.status_code}"
        else:
            data = response.json()

            if not isinstance(data, list):
                result = BOT_MESSAGES["api_error"]
            else:
                if is_gainers:
                    sorted_data = sorted(data, key=lambda x: x.get('price_change_percentage_24h', 0) or 0, reverse=True)[:5]
                    title = f"{EMOJIS['rocket']} Топ роста за 24ч:\n\n"
                else:
                    sorted_data = sorted(data, key=lambda x: x.get('price_change_percentage_24h', 0) or 0)[:5]
                    title = f"{EMOJIS['fire']} Топ падения за 24ч:\n\n"

                result = title
                for i, crypto in enumerate(sorted_data, 1):
                    if not isinstance(crypto, dict):
                        continue

                    change = crypto.get('price_change_percentage_24h', 0) or 0
                    result += f"{i}. {crypto.get('symbol', 'N/A').upper()}\n"
                    result += f"   {EMOJIS['money']} ${crypto.get('current_price', 0):,.2f}\n"
                    result += f"   📊 {change:+.2f}%\n\n"

        price_cache[cache_key] = (result, time.time())
        return result

    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(BOT_MESSAGES["welcome"], reply_markup=get_main_keyboard())

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(BOT_MESSAGES["help"])

@dp.message(Command("graph"))
async def cmd_graph(message: types.Message):
    if len(message.text.split()) > 1:
        crypto_name = message.text.split()[1].lower()
        await message.answer("📊 Генерирую график...")

        chart_buffer = await generate_price_chart(crypto_name, days=7)

        if chart_buffer:
            await message.answer_photo(
                types.BufferedInputFile(chart_buffer.getvalue(), filename="chart.png"),
                caption=f"📈 График {crypto_name.upper()} за 7 дней"
            )
        else:
            await message.answer("❌ Не удалось сгенерировать график")
    else:
        await message.answer("ℹ️ Использование: /graph bitcoin")

@dp.message(Command("cache"))
async def cmd_cache(message: types.Message):
    price_cache.clear()
    await message.answer("🔄 Кэш очищен")

@dp.message(lambda message: message.text in ["📊 Курсы", "Курсы"])
async def show_prices(message: types.Message):
    await message.answer("Выбери криптовалюту:", reply_markup=get_crypto_keyboard())

@dp.message(lambda message: message.text in ["🏆 Топ-5", "Топ-5"])
async def show_top5(message: types.Message):
    await message.answer(await get_top_cryptos(5))

@dp.message(lambda message: message.text in ["🚀 Рост", "Рост"])
async def show_gainers(message: types.Message):
    await message.answer(await get_movers(True))

@dp.message(lambda message: message.text in ["💥 Падение", "Падение"])
async def show_losers(message: types.Message):
    await message.answer(await get_movers(False))

@dp.callback_query(lambda callback: callback.data.startswith('price_'))
async def process_crypto(callback: types.CallbackQuery):
    crypto_ticker = callback.data.split('_')[1]
    crypto_id = POPULAR_CRYPTO.get(crypto_ticker)

    if crypto_id:
        price_info = await get_crypto_price(crypto_id)
        await callback.message.answer(price_info, reply_markup=get_chart_keyboard(crypto_ticker))

    await callback.answer()

@dp.callback_query(lambda callback: callback.data.startswith('chart_'))
async def show_chart(callback: types.CallbackQuery):
    crypto_ticker = callback.data.split('_')[1]
    crypto_id = POPULAR_CRYPTO.get(crypto_ticker)

    if not crypto_id:
        await callback.answer("❌ Монета не найдена")
        return

    await callback.message.answer("📊 Генерирую график...")

    chart_buffer = await generate_price_chart(crypto_id, days=7)

    if chart_buffer:
        await callback.message.answer_photo(
            types.BufferedInputFile(chart_buffer.getvalue(), filename="chart.png"),
            caption=f"📈 График {crypto_id.upper()} за 7 дней"
        )
    else:
        await callback.message.answer("❌ Не удалось сгенерировать график")

    await callback.answer()

@dp.callback_query(lambda callback: callback.data.startswith('chart30_'))
async def show_chart_30d(callback: types.CallbackQuery):
    crypto_ticker = callback.data.split('_')[1]
    crypto_id = POPULAR_CRYPTO.get(crypto_ticker)

    if not crypto_id:
        await callback.answer("❌ Монета не найдена")
        return

    await callback.message.answer("📊 Генерирую график за 30 дней...")

    chart_buffer = await generate_price_chart(crypto_id, days=30)

    if chart_buffer:
        await callback.message.answer_photo(
            types.BufferedInputFile(chart_buffer.getvalue(), filename="chart30.png"),
            caption=f"📈 График {crypto_id.upper()} за 30 дней"
        )
    else:
        await callback.message.answer("❌ Не удалось сгенерировать график")

    await callback.answer()

@dp.message()
async def handle_text(message: types.Message):
    text = message.text.strip().lower()

    if text in [cmd.lower() for cmd in MENU_COMMANDS]:
        return

    if text.startswith('/'):
        return

    if len(text) > 30:
        return

    russian_chars = any(char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for char in text)
    if russian_chars:
        return

    price_info = await get_crypto_price(text)
    await message.answer(price_info)

async def main():
    print("🤖 Запуск бота...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")

if __name__ == '__main__':
    asyncio.run(main())