from aiogram.fsm.state import State, StatesGroup

class ConverterStates(StatesGroup):
    selecting_from = State()
    selecting_to = State()
    entering_amount = State()

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import BOT_MESSAGES, CONVERT_CURRENCIES
from keyboards import get_currency_type_keyboard, get_crypto_currency_keyboard, get_cancel_keyboard
from api.coingecko import convert_currency

router = Router()

@router.message(Command("convert"))
async def cmd_convert(message: types.Message, state: FSMContext):
    await state.set_state(ConverterStates.selecting_from)
    await message.answer(
        BOT_MESSAGES["select_from_currency"],
        reply_markup=get_currency_type_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text.in_(["💱 Конвертер", "Конвертер"]))
async def show_converter(message: types.Message, state: FSMContext):
    await state.set_state(ConverterStates.selecting_from)
    await message.answer(
        BOT_MESSAGES["select_from_currency"],
        reply_markup=get_currency_type_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith('convert_type_'))
async def process_currency_type(callback: types.CallbackQuery, state: FSMContext):
    currency_type = callback.data.split('_')[2]

    await state.update_data(currency_type=currency_type)

    current_state = await state.get_state()

    if current_state == ConverterStates.selecting_from.state:
        await callback.message.edit_text(
            "📥 Выберите <b>исходную валюту</b>:",
            reply_markup=get_crypto_currency_keyboard(currency_type, "from"),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "📤 Выберите <b>целевую валюту</b>:",
            reply_markup=get_crypto_currency_keyboard(currency_type, "to"),
            parse_mode="HTML"
        )

    await callback.answer()

@router.callback_query(F.data.startswith('convert_from_'))
async def process_from_currency(callback: types.CallbackQuery, state: FSMContext):
    currency_ticker = callback.data.split('_')[2]
    user_data = await state.get_data()

    await state.update_data(from_currency=currency_ticker)
    await state.set_state(ConverterStates.selecting_to)

    currency_type = user_data.get('currency_type', 'crypto')
    await state.update_data(from_currency_type=currency_type)

    await callback.message.edit_text(
        BOT_MESSAGES["select_to_currency"],
        reply_markup=get_currency_type_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()

@router.callback_query(F.data.startswith('convert_to_'))
async def process_to_currency(callback: types.CallbackQuery, state: FSMContext):
    currency_ticker = callback.data.split('_')[2]
    user_data = await state.get_data()

    from_currency = user_data.get('from_currency')

    if from_currency == currency_ticker:
        await callback.answer(BOT_MESSAGES["convert_same_currency"], show_alert=True)
        return

    await state.update_data(to_currency=currency_ticker)
    await state.set_state(ConverterStates.entering_amount)

    from_type = user_data.get('from_currency_type', 'crypto')
    to_type = user_data.get('currency_type', 'crypto')

    from_display = CONVERT_CURRENCIES[from_type].get(from_currency, from_currency.upper())
    to_display = CONVERT_CURRENCIES[to_type].get(currency_ticker, currency_ticker.upper())

    if from_type == 'crypto':
        from_display = f"{from_currency.upper()} ({from_display})"
    if to_type == 'crypto':
        to_display = f"{currency_ticker.upper()} ({to_display})"

    await state.update_data(
        from_display=from_display,
        to_display=to_display,
        from_type=from_type,
        to_type=to_type
    )

    await callback.message.edit_text(
        f"💰 Введите сумму в <b>{from_display}</b> для конвертации в <b>{to_display}</b>:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()

@router.callback_query(F.data == 'convert_back_type')
async def process_back_to_type(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == ConverterStates.selecting_to.state:
        await state.set_state(ConverterStates.selecting_from)

    await callback.message.edit_text(
        BOT_MESSAGES["select_from_currency"],
        reply_markup=get_currency_type_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()

@router.callback_query(F.data == 'convert_cancel')
async def process_convert_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Конвертация отменена",
        reply_markup=None
    )
    await callback.answer()

@router.message(ConverterStates.entering_amount)
async def process_amount_input(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))

        if amount <= 0:
            await message.answer(BOT_MESSAGES["convert_invalid_amount"])
            return

        user_data = await state.get_data()

        from_currency = user_data['from_currency']
        to_currency = user_data['to_currency']
        from_type = user_data.get('from_type', 'crypto')
        to_type = user_data.get('to_type', 'crypto')

        if from_type == 'crypto':
            from_id = CONVERT_CURRENCIES['crypto'][from_currency]
        else:
            from_id = from_currency

        if to_type == 'crypto':
            to_id = CONVERT_CURRENCIES['crypto'][to_currency]
        else:
            to_id = to_currency

        await message.answer("🔄 Конвертирую...")
        converted_amount, status = await convert_currency(amount, from_id, to_id)

        if status == "error" or converted_amount is None:
            await message.answer(BOT_MESSAGES["convert_error"])
        else:
            result = format_conversion_result(
                amount,
                user_data['from_display'],
                converted_amount,
                user_data['to_display']
            )
            await message.answer(result, parse_mode="HTML")

        await message.answer(
            f"💰 Введите новую сумму в <b>{user_data['from_display']}</b> или нажмите /start для выхода:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )

    except ValueError:
        await message.answer(
            BOT_MESSAGES["convert_invalid_amount"],
            reply_markup=get_cancel_keyboard()
        )
    except Exception as e:
        print(f"Ошибка конвертации: {e}")
        await message.answer(BOT_MESSAGES["convert_error"])
        await state.clear()

def format_conversion_result(amount: float, from_display: str, converted_amount: float, to_display: str) -> str:
    def format_number(value):
        if value < 0.000001:
            return f"{value:.8f}"
        elif value < 0.001:
            return f"{value:.6f}"
        elif value < 1:
            return f"{value:.4f}"
        elif value < 1000:
            return f"{value:.2f}"
        else:
            return f"{value:,.0f}"

    formatted_from = format_number(amount)
    formatted_to = format_number(converted_amount)
    rate = format_number(converted_amount / amount)

    return (
        f"💱 <b>Результат конвертации:</b>\n\n"
        f"📥 {formatted_from} {from_display}\n"
        f"⬇️\n"
        f"📤 {formatted_to} {to_display}\n\n"
        f"<i>Курс: 1 {from_display.split(' ')[0]} = {rate} {to_display.split(' ')[0]}</i>"
    )