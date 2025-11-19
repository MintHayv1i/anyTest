from aiogram.fsm.state import State, StatesGroup

class ConverterStates(StatesGroup):
    selecting_from = State()
    selecting_to = State()
    entering_amount = State()