import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import config
from handlers import setup_handlers
from data_storage import set_bot_commands


async def main() -> None: # Запуск команды
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    await set_bot_commands(bot)
    setup_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    print("Бот запущен...")
    asyncio.run(main())
