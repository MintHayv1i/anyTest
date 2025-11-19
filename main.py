import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.commands import router as commands_router
from handlers.callbacks import router as callbacks_router
from handlers.messages import router as messages_router
from handlers.converter import router as converter_router

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(commands_router)
dp.include_router(callbacks_router)
dp.include_router(messages_router)
dp.include_router(converter_router)

async def main():
    print("🤖 Запуск бота...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")

if __name__ == '__main__':
    asyncio.run(main())