import json
from typing import Dict, Any
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Определяем структуру данных с полем chat_id
default_data: Dict[str, Any] = {
    "schedule": [],
    "habits": [],
    "mood_log": [],
    "chat_id": 7944636649
}

data: Dict[str, Any] = default_data.copy()

def load_data() -> Dict[str, Any]:
    """
    Загружает данные из файла data.json, добавляя недостающие поля.
    """
    global data
    logger.info("Loading data from data.json")
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            loaded_data = json.load(file)
            logger.info(f"Loaded data: {loaded_data}")
            # Добавляем недостающие поля из default_data
            for key, value in default_data.items():
                if key not in loaded_data:
                    loaded_data[key] = value
            data = loaded_data
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("data.json not found or invalid, returning default data")
        data = default_data.copy()
        save_data()  # Создаем файл с начальными данными
        return data

def save_data() -> None:
    """
    Сохраняет данные в файл data.json
    """
    logger.info(f"Saving data to data.json: {data}")
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    logger.info("Data saved successfully")

async def set_bot_commands(bot) -> None:
    """
    Устанавливает команды для бота
    """
    logger.info("Setting bot commands")
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/help", description="Показать список команд"),
        BotCommand(command="/dobavit_sobytie", description="Добавить событие в расписание"),
        BotCommand(command="/raspisanue", description="Показать расписание"),
        BotCommand(command="/udalit_sobytie", description="Удалить событие из расписания"),
        BotCommand(command="/dobavit_privychku", description="Добавить новую привычку"),
        BotCommand(command="/privychki", description="Показать список привычек"),
        BotCommand(command="/dobavit_nastroenie", description="Записать настроение"),
        BotCommand(command="/nastroenie", description="Показать записи настроения"),
        BotCommand(command="/otmena", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands set successfully")