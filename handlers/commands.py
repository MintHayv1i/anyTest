from aiogram import Router, types, F
from aiogram.filters import Command

from config import BOT_MESSAGES
from keyboards import get_main_keyboard, get_crypto_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        BOT_MESSAGES["start"],
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        BOT_MESSAGES["help"],
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("rates"))
async def cmd_rates(message: types.Message):
    await message.answer("💰 Выберите криптовалюту:", reply_markup=get_crypto_keyboard())


@router.message(Command("news"))
async def cmd_news(message: types.Message):
    """Команда новостей"""
    from api.news import get_daily_news
    from keyboards import get_news_keyboard

    await message.answer("📡 Загружаю свежие новости...")

    news_text = await get_daily_news()

    await message.answer(
        news_text,
        reply_markup=get_news_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )