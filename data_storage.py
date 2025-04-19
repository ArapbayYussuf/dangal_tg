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
    Команды для бота
    """
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="/start", description="Приветствие"),
        BotCommand(command="/add_event", description="Добавить новое событие"),
        BotCommand(command="/schedule", description="Показать текущее расписание"),
        BotCommand(command="/remove_event", description="Удалить событие"),
        BotCommand(command="/add_habit", description="Добавить привычку"),
        BotCommand(command="/habits", description="Показать привычки"),
        BotCommand(command="/add_mood", description="Добавить настроение"),
        BotCommand(command="/mood", description="Показать записи о настроении")
    ]
    await bot.set_my_commands(commands)
