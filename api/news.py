import aiohttp
import asyncio
from datetime import datetime, timedelta
from config import NEWSAPI_KEY


async def get_daily_news(limit: int = 5):
    """Умный поиск новостей - несколько стратегий"""
    try:
        if not NEWSAPI_KEY:
            return "❌ Добавьте NEWSAPI_KEY в .env файл"

        strategies = [
            # Стратегия 1: Топовые новости бизнеса
            {
                'url': "https://newsapi.org/v2/top-headlines",
                'params': {
                    'category': 'business',
                    'language': 'en',
                    'pageSize': limit,
                    'q': 'crypto OR bitcoin OR ethereum'
                },
                'name': 'Топовые бизнес-новости'
            },
            # Стратегия 2: Общий поиск за 3 дня
            {
                'url': "https://newsapi.org/v2/everything",
                'params': {
                    'q': 'bitcoin OR ethereum OR cryptocurrency OR blockchain',
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': limit,
                    'from': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
                },
                'name': 'Общий поиск за 3 дня'
            },
            # Стратегия 3: Поиск по популярным источникам
            {
                'url': "https://newsapi.org/v2/everything",
                'params': {
                    'q': 'crypto OR bitcoin',
                    'language': 'en',
                    'sortBy': 'relevancy',
                    'pageSize': limit,
                    'domains': 'cointelegraph.com,coindesk.com,decrypt.co,bloomberg.com,reuters.com'
                },
                'name': 'Поиск по популярным источникам'
            },
            # Стратегия 4: Широкий поиск без ограничений
            {
                'url': "https://newsapi.org/v2/everything",
                'params': {
                    'q': 'cryptocurrency',
                    'language': 'en',
                    'sortBy': 'popularity',
                    'pageSize': limit,
                    'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                },
                'name': 'Широкий поиск'
            }
        ]

        async with aiohttp.ClientSession() as session:
            for strategy in strategies:
                try:
                    print(f"🔍 Пробуем стратегию: {strategy['name']}")

                    params = strategy['params'].copy()
                    params['apiKey'] = NEWSAPI_KEY

                    async with session.get(strategy['url'], params=params, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()

                            # Дебаг информация
                            total_results = data.get('totalResults', 0)
                            articles_count = len(data.get('articles', []))
                            print(f"📊 Найдено: {total_results} всего, {articles_count} статей")

                            if data.get('articles'):
                                print(f"✅ Успех с стратегией: {strategy['name']}")
                                if articles_count > 0:
                                    print(f"📰 Первая статья: {data['articles'][0].get('title', 'No title')[:50]}...")
                                return format_news_message(data['articles'][:limit])
                            else:
                                print(f"❌ В стратегии {strategy['name']} статьи не найдены")
                        else:
                            error_data = await response.json()
                            print(
                                f"❌ HTTP {response.status} в стратегии {strategy['name']}: {error_data.get('message', 'Unknown error')}")

                except asyncio.TimeoutError:
                    print(f"⏰ Таймаут в стратегии: {strategy['name']}")
                    continue
                except Exception as e:
                    print(f"⚠️ Ошибка в стратегии {strategy['name']}: {e}")
                    continue

        return "📰 Не удалось найти крипто-новости ни по одной из стратегий"

    except Exception as e:
        return f"❌ Критическая ошибка: {str(e)}"


def format_news_message(articles):
    """Форматирует РЕАЛЬНЫЕ новости"""
    if not articles:
        return "📰 Новостей не найдено"

    message = "📰 <b>СВЕЖИЕ НОВОСТИ КРИПТОРЫНКА</b>\n\n"

    for i, article in enumerate(articles, 1):
        title = article.get('title', 'Без названия')
        url = article.get('url', '#')
        source = article.get('source', {}).get('name', 'Unknown')
        description = article.get('description', '')
        published = article.get('publishedAt', '')

        # Пропускаем статьи без заголовка или с [Removed]
        if not title or title == '[Removed]':
            continue

        # Обрезаем длинные заголовки
        if len(title) > 80:
            title = title[:77] + "..."

        # Анализ тональности на основе заголовка
        emoji = get_sentiment_emoji(title)

        message += f"{emoji} <b>{title}</b>\n"

        if description and description != '[Removed]' and len(description) > 50:
            message += f"   📝 {description[:100]}...\n"

        message += f"   📖 {source}\n"

        # Форматируем время
        if published:
            time_str = format_published_time(published)
            message += f"   🕒 {time_str}\n"

        message += f"   🔗 <a href='{url}'>Читать полностью</a>\n\n"

    # Если после фильтрации не осталось статей
    if message == "📰 <b>СВЕЖИЕ НОВОСТИ КРИПТОРЫНКА</b>\n\n":
        return "📰 Все найденные статьи были отфильтрованы (пустые или удаленные)"

    message += f"⏰ <i>Обновлено: {datetime.now().strftime('%H:%M')}</i>"
    return message


def get_sentiment_emoji(title):
    """Определяет эмодзи по тональности заголовка"""
    title_lower = title.lower()

    positive_words = ['surge', 'rise', 'growth', 'bullish', 'gain', 'вырос', 'рост', 'успех', 'up', 'high', 'rally']
    negative_words = ['drop', 'fall', 'crash', 'bearish', 'loss', 'упал', 'падение', 'снижение', 'down', 'low',
                      'plunge']
    warning_words = ['warning', 'alert', 'risk', 'опасность', 'предупреждение', 'fraud', 'scam']

    if any(word in title_lower for word in positive_words):
        return "🟢"
    elif any(word in title_lower for word in negative_words):
        return "🔻"
    elif any(word in title_lower for word in warning_words):
        return "⚠️"
    else:
        return "ℹ️"


def format_published_time(published_str):
    """Форматирует время публикации"""
    try:
        # Обрабатываем разные форматы времени
        if published_str.endswith('Z'):
            pub_time = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
        else:
            pub_time = datetime.fromisoformat(published_str)

        now = datetime.now(pub_time.tzinfo) if pub_time.tzinfo else datetime.now()

        diff = now - pub_time
        hours = diff.total_seconds() // 3600

        if hours < 1:
            return "Только что"
        elif hours < 24:
            return f"{int(hours)} ч. назад"
        else:
            days = int(hours // 24)
            return f"{days} д. назад"
    except:
        return "Недавно"


# Пример использования для тестирования
async def test_news():
    """Функция для тестирования работы новостей"""
    print("🧪 Тестируем получение новостей...")
    result = await get_daily_news(3)
    print("Результат:")
    print(result)


if __name__ == "__main__":
    # Запуск теста
    asyncio.run(test_news())