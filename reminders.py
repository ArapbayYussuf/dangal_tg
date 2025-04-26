import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from data_storage import data, save_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_reminders(bot: Bot) -> None:
    """
    Периодически проверяет расписание и отправляет напоминания за 10 минут до события.
    """
    logger.info("Начало проверки напоминаний")
    while True:
        current_time = datetime.now()
        logger.debug(f"Текущее время: {current_time.strftime('%H:%M:%S')}")

        for event in data["schedule"]:
            try:
                if not all(key in event for key in ["time", "name", "chat_id"]):
                    logger.warning(f"Некорректное событие: {event}. Пропускаем.")
                    continue

                event_time = datetime.strptime(event["time"], "%H:%M")
                event_time = current_time.replace(
                    hour=event_time.hour, minute=event_time.minute, second=0, microsecond=0
                )
                time_diff = (event_time - current_time).total_seconds() / 60
                logger.debug(
                    f"Событие: {event['name']} в {event['time']}, разница: {time_diff:.2f} минут, notified: {event.get('notified')}")

                if 9 <= time_diff <= 11 and not event.get("notified", False):
                    logger.info(f"Отправка напоминания для {event['name']} в чат {event['chat_id']}")
                    await bot.send_message(
                        chat_id=event["chat_id"],
                        text=f"⏰ *Напоминание!* Через 10 минут: *{event['name']}* в {event['time']}",
                        parse_mode="Markdown"
                    )
                    event["notified"] = True
                    save_data()
                elif time_diff < -1 and event.get("notified", False):
                    event["notified"] = False
                    logger.debug(f"Сброс notified для события: {event['name']}")
                    save_data()
            except ValueError as e:
                logger.error(f"Ошибка формата времени для события {event.get('name', 'Unknown')}: {e}")
                continue
            except Exception as e:
                logger.error(f"Общая ошибка при обработке события {event.get('name', 'Unknown')}: {e}")
                continue

        await asyncio.sleep(10)  # Проверяем каждые 10 секунд для точности