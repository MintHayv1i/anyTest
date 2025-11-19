import requests
import matplotlib.pyplot as plt
import io
from datetime import datetime

from config import COINGECKO_API_URL

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