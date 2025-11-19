from aiogram import Router, types, F
from aiogram.types import BufferedInputFile
from config import CRYPTO_CURRENCIES
from api.coingecko import get_crypto_price, get_top_cryptos, get_movers
from api.charts import generate_price_chart
from keyboards import get_chart_keyboard, get_news_keyboard, get_main_keyboard
from config import BOT_MESSAGES

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
    days = int(callback.data.split('_')[1])
    message_text = callback.message.text
    crypto_id = None
    for crypto in CRYPTO_CURRENCIES:
        if crypto in message_text.lower():
            crypto_id = crypto
            break
    if not crypto_id:
        await callback.answer("❌ Ошибка")
        return
    await callback.message.answer(f"📊 Генерирую график за {days} дней...")
    chart_buffer = await generate_price_chart(crypto_id, days=days)
    if chart_buffer:
        await callback.message.answer_photo(
            BufferedInputFile(chart_buffer.getvalue(), filename="chart.png"),
            caption=f"📈 {crypto_id.upper()} за {days} дней"
        )
    else:
        await callback.message.answer("❌ Ошибка графика")
    await callback.answer()


@router.callback_query(F.data.startswith('top_'))
async def show_top_cryptos(callback: types.CallbackQuery):
    limit = int(callback.data.split('_')[1])
    top_info = await get_top_cryptos(limit)
    await callback.message.edit_text(top_info)
    await callback.answer()


@router.callback_query(F.data == 'gainers')
async def show_gainers(callback: types.CallbackQuery):
    gainers_info = await get_movers(is_gainers=True)
    await callback.message.edit_text(gainers_info)
    await callback.answer()


@router.callback_query(F.data == 'losers')
async def show_losers(callback: types.CallbackQuery):
    losers_info = await get_movers(is_gainers=False)
    await callback.message.edit_text(losers_info)
    await callback.answer()


# НОВОСТИ - УПРОЩЕННАЯ ВЕРСИЯ
@router.callback_query(F.data == 'news_refresh')
async def refresh_news(callback: types.CallbackQuery):
    """Обновить новости"""
    from api.news import get_daily_news

    await callback.message.edit_text("📡 Загружаю свежие новости...")

    news_text = await get_daily_news()

    await callback.message.edit_text(
        news_text,
        reply_markup=get_news_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        BOT_MESSAGES["start"],
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()