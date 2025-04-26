import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from data_storage import data

async def check_reminders(bot: Bot) -> None:
    """
    Периодически проверяет расписание и отправляет напоминания за 10 минут до события.
    """
    while True:
        current_time = datetime.now()
        for event in data["schedule"]:
            try:
                event_time = datetime.strptime(event["time"], "%H:%M")
                # Сравниваем только время (игнорируем дату, так как дата не хранится)
                event_time = current_time.replace(
                    hour=event_time.hour, minute=event_time.minute, second=0, microsecond=0
                )
                time_diff = (event_time - current_time).total_seconds() / 60

                # Проверяем, осталось ли 10 минут (±1 минута для точности)
                if 9 <= time_diff <= 11 and event.get("notified") != True:
                    chat_id = event.get("chat_id")
                    if chat_id:
                        await bot.send_message(
                            chat_id=chat_id,
                            text=f"⏰ Напоминание! Через 10 минут: {event['name']} в {event['time']}"
                        )
                        event["notified"] = True  # Помечаем, чтобы не отправлять повторно
            except (ValueError, KeyError) as e:
                # Игнорируем ошибки формата времени или отсутствия chat_id
                continue

        # Сбрасываем флаг notified для событий на следующий день
        for event in data["schedule"]:
            try:
                event_time = datetime.strptime(event["time"], "%H:%M")
                event_time = current_time.replace(
                    hour=event_time.hour, minute=event_time.minute, second=0, microsecond=0
                )
                if current_time > event_time:
                    event["notified"] = False
            except ValueError:
                continue

        await asyncio.sleep(60)  # Проверяем каждую минуту