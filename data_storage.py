import json
from typing import Dict, Any

data: Dict[str, Any] = {
    "schedule": [],
    "habits": [],
    "mood_log": []
}

def load_data() -> Dict[str, Any]:
    """
    Загружает данные из файла data.json
    """
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"schedule": [], "habits": [], "mood_log": []}

def save_data() -> None:
    """
    Сохраняет данные в файл data.json
    """
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

async def set_bot_commands(bot) -> None:
    """
    Устанавливает команды для бота
    """
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
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