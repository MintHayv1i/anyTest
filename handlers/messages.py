from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from keyboards import get_main_keyboard, get_crypto_keyboard, get_currency_type_keyboard, get_news_keyboard
from api.coingecko import get_crypto_price, get_top_cryptos, get_movers
from handlers.converter import ConverterStates

router = Router()


@router.message(F.text.contains("Курсы"))
async def show_rates(message: types.Message):
    await message.answer("💰 Выберите криптовалюту:", reply_markup=get_crypto_keyboard())


@router.message(F.text.contains("Конвертер"))
async def show_converter(message: types.Message, state: FSMContext):
    await state.set_state(ConverterStates.selecting_from)
    await message.answer(
        "💱 <b>Конвертер валют</b>\n\nВыберите тип валюты:",
        reply_markup=get_currency_type_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text.contains("Топ"))
async def show_top(message: types.Message):
    from keyboards import get_top_keyboard
    await message.answer("📈 Выберите количество:", reply_markup=get_top_keyboard())


@router.message(F.text.contains("Рост"))
async def show_gainers(message: types.Message):
    gainers_info = await get_movers(is_gainers=True)
    await message.answer(gainers_info)


@router.message(F.text.contains("Падение"))
async def show_losers(message: types.Message):
    losers_info = await get_movers(is_gainers=False)
    await message.answer(losers_info)


@router.message(F.text.contains("Новости"))
async def show_news(message: types.Message):
    """Показать новости"""
    from api.news import get_daily_news

    await message.answer("📡 Загружаю свежие новости...")

    news_text = await get_daily_news()

    await message.answer(
        news_text,
        reply_markup=get_news_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.message(F.text.contains("Помощь"))
async def show_help(message: types.Message):
    from config import BOT_MESSAGES
    await message.answer(BOT_MESSAGES["help"], parse_mode="HTML")