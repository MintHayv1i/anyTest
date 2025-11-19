from aiogram import Router, types, F
from aiogram.types import BufferedInputFile

from config import CRYPTO_CURRENCIES
from api.coingecko import get_crypto_price
from api.charts import generate_price_chart
from keyboards import get_chart_keyboard

router = Router()


@router.callback_query(F.data.startswith('price_'))
async def process_crypto(callback: types.CallbackQuery):
    crypto_id = callback.data.split('_')[1]

    if crypto_id in CRYPTO_CURRENCIES:
        price_info = await get_crypto_price(crypto_id)
        await callback.message.answer(price_info, reply_markup=get_chart_keyboard())

    await callback.answer()


@router.callback_query(F.data.startswith('chart_'))
async def show_chart(callback: types.CallbackQuery):
    parts = callback.data.split('_')
    days = int(parts[1])

    # Получаем последнюю выбранную криптовалюту из текста сообщения
    message_text = callback.message.text
    crypto_id = None

    # Пытаемся извлечь ID криптовалюты из текста сообщения
    for crypto in CRYPTO_CURRENCIES:
        if crypto in message_text.lower():
            crypto_id = crypto
            break

    if not crypto_id:
        await callback.answer("❌ Не удалось определить криптовалюту")
        return

    await callback.message.answer(f"📊 Генерирую график за {days} дней...")
    chart_buffer = await generate_price_chart(crypto_id, days=days)

    if chart_buffer:
        await callback.message.answer_photo(
            BufferedInputFile(chart_buffer.getvalue(), filename=f"chart_{days}d.png"),
            caption=f"📈 График {crypto_id.upper()} за {days} дней"
        )
    else:
        await callback.message.answer("❌ Не удалось сгенерировать график")

    await callback.answer()


@router.callback_query(F.data.startswith('top_'))
async def show_top_cryptos(callback: types.CallbackQuery):
    from api.coingecko import get_top_cryptos

    limit = int(callback.data.split('_')[1])
    top_info = await get_top_cryptos(limit)

    await callback.message.edit_text(top_info)
    await callback.answer()


@router.callback_query(F.data == 'gainers')
async def show_gainers(callback: types.CallbackQuery):
    from api.coingecko import get_movers

    gainers_info = await get_movers(is_gainers=True)
    await callback.message.edit_text(gainers_info)
    await callback.answer()


@router.callback_query(F.data == 'losers')
async def show_losers(callback: types.CallbackQuery):
    from api.coingecko import get_movers

    losers_info = await get_movers(is_gainers=False)
    await callback.message.edit_text(losers_info)
    await callback.answer()