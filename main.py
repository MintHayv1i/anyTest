import asyncio
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.commands import router as commands_router
from handlers.callbacks import router as callbacks_router
from handlers.messages import router as messages_router
from handlers.converter import router as converter_router

# Проверяем что бот не запущен рекурсивно
if getattr(sys, 'frozen', False):
    # Если запущен как exe
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

print(f"🔄 Запуск из: {base_path}")

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
        # Останавливаем любые предыдущие обновления
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Вебхук удален, старые обновления очищены")

        # Проверяем соединение с Telegram
        me = await bot.get_me()
        print(f"✅ Бот @{me.username} успешно подключен")

        # Запускаем поллинг
        await dp.start_polling(bot)

    except Exception as e:
        print(f"❌ Критическая ошибка бота: {e}")
        print("🔄 Перезапуск через 5 секунд...")
        await asyncio.sleep(5)
        await main()  # Рекурсивный перезапуск


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("❌ Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")