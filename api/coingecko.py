import asyncio
import time
import requests
from datetime import datetime

from config import COINGECKO_API_URL, REQUEST_DELAY, BOT_MESSAGES, EMOJIS, CURRENCIES
from utils.cache import price_cache


def make_sync_api_request(url: str, params: dict):
    """Синхронный запрос к API"""
    try:
        response = requests.get(url, params=params, timeout=15)
        return response
    except requests.exceptions.Timeout:
        raise Exception("Таймаут запроса")
    except requests.exceptions.ConnectionError:
        raise Exception("Ошибка подключения")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка запроса: {str(e)}")


def normalize_currency_name(currency: str):
    """Приводит названия валют к стандартному формату"""
    currency = currency.lower().strip()

    # Криптовалюты
    crypto_map = {
        'btc': 'bitcoin', 'bitcoin': 'bitcoin',
        'eth': 'ethereum', 'ethereum': 'ethereum',
        'sol': 'solana', 'solana': 'solana',
        'bnb': 'binancecoin', 'binance': 'binancecoin',
        'xrp': 'ripple', 'ripple': 'ripple',
        'ada': 'cardano', 'cardano': 'cardano',
        'doge': 'dogecoin', 'dogecoin': 'dogecoin',
        'dot': 'polkadot', 'polkadot': 'polkadot',
        'matic': 'polygon-pos', 'polygon': 'polygon-pos',
        'avax': 'avalanche-2', 'avalanche': 'avalanche-2'
    }

    # Фиатные валюты
    fiat_map = {
        'usd': 'usd', 'доллар': 'usd', '$': 'usd',
        'rub': 'rub', 'рубль': 'rub', '₽': 'rub',
        'eur': 'eur', 'евро': 'eur', '€': 'eur',
        'kzt': 'kzt', 'тенге': 'kzt',
        'uah': 'uah', 'гривна': 'uah', '₴': 'uah'
    }

    if currency in crypto_map:
        return crypto_map[currency]
    elif currency in fiat_map:
        return fiat_map[currency]
    else:
        return currency


async def get_crypto_price(crypto_id: str):
    """Получает цену криптовалюты"""
    cache_key = f"price_{crypto_id}"
    if cache_key in price_cache:
        cache_data, cache_timestamp = price_cache[cache_key]
        if time.time() - cache_timestamp < 60:
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
    """Получает топ криптовалют по капитализации"""
    cache_key = f"top_{limit}"
    if cache_key in price_cache:
        cache_data, cache_timestamp = price_cache[cache_key]
        if time.time() - cache_timestamp < 60:
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
    """Получает топ роста или падения"""
    cache_key = f"movers_{'up' if is_gainers else 'down'}"
    if cache_key in price_cache:
        cache_data, cache_timestamp = price_cache[cache_key]
        if time.time() - cache_timestamp < 60:
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
                    sorted_data = sorted(data, key=lambda x: x.get('price_change_percentage_24h', 0) or 0,
                                         reverse=True)[:5]
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


async def convert_currency(amount: float, from_curr: str, to_curr: str):
    """Конвертирует между любыми валютами"""
    try:
        from_curr = normalize_currency_name(from_curr)
        to_curr = normalize_currency_name(to_curr)

        print(f"DEBUG: Converting {amount} from {from_curr} to {to_curr}")

        if from_curr == to_curr:
            return None, "same_currency"

        # Для крипто-крипто и крипто-фиат конвертации
        url = f"{COINGECKO_API_URL}/simple/price"
        params = {
            'ids': from_curr,
            'vs_currencies': to_curr
        }

        response = await asyncio.get_event_loop().run_in_executor(
            None, make_sync_api_request, url, params
        )

        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: API response: {data}")

            if from_curr in data:
                rate = data[from_curr].get(to_curr, 0)
                print(f"DEBUG: Conversion rate: {rate}")

                if rate > 0:
                    return amount * rate, "success"

        # Если не получилось через simple/price, пробуем через прямую конвертацию
        return await direct_currency_conversion(amount, from_curr, to_curr)

    except Exception as e:
        print(f"Ошибка конвертации: {e}")
        return None, "error"


async def direct_currency_conversion(amount: float, from_curr: str, to_curr: str):
    """Прямая конвертация через другой endpoint"""
    try:
        # Для фиат-фиат конвертации используем другой подход
        url = f"{COINGECKO_API_URL}/simple/price"

        # Если обе валюты фиатные, используем bitcoin как промежуточную
        if from_curr in ['usd', 'rub', 'eur', 'kzt', 'uah'] and to_curr in ['usd', 'rub', 'eur', 'kzt', 'uah']:
            params = {
                'ids': 'bitcoin',
                'vs_currencies': f"{from_curr},{to_curr}"
            }

            response = await asyncio.get_event_loop().run_in_executor(
                None, make_sync_api_request, url, params
            )

            if response.status_code == 200:
                data = response.json()
                if 'bitcoin' in data:
                    btc_data = data['bitcoin']
                    rate_from = btc_data.get(from_curr, 0)
                    rate_to = btc_data.get(to_curr, 0)

                    if rate_from > 0 and rate_to > 0:
                        # Конвертируем через BTC
                        btc_amount = amount / rate_from
                        converted_amount = btc_amount * rate_to
                        return converted_amount, "success"

        return None, "error"

    except Exception as e:
        print(f"Ошибка прямой конвертации: {e}")
        return None, "error"