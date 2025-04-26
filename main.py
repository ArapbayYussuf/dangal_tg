import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import config
from handlers import setup_handlers
from data_storage import set_bot_commands
from reminders import Reminder
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main() -> None:
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    reminder = Reminder(bot)
    reminder.setup()

    await set_bot_commands(bot)
    setup_handlers(dp, reminder)

    try:
        await dp.start_polling(bot)
    finally:
        reminder.shutdown()
        await bot.session.close()

if __name__ == "__main__":
    print("Бот запущен...")
    asyncio.run(main())