from aiogram import Router, types, F
from aiogram.filters import Command

from config import BOT_MESSAGES
from keyboards import get_main_keyboard, get_crypto_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(BOT_MESSAGES["start"], reply_markup=get_main_keyboard())

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(BOT_MESSAGES["help"], reply_markup=get_main_keyboard())

@router.message(Command("rates"))
async def cmd_rates(message: types.Message):
    await message.answer("💰 Выберите криптовалюту:", reply_markup=get_crypto_keyboard())