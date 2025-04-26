from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from data_storage import load_data, save_data
from typing import Dict, Any
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация планировщика
scheduler = AsyncIOScheduler()

class Reminder:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.setted_up = False
        self.data: Dict[str, Any] = load_data()

    def setup(self):
        """
        Настраивает планировщик для напоминаний.
        """
        logger.info("Starting scheduler setup...")
        scheduler.start()
        logger.info("Scheduler started.")
        self.schedule_reminders()
        self.setted_up = True
        logger.info("Reminder setup completed.")

    def shutdown(self):
        """
        Останавливает планировщик.
        """
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        self.setted_up = False
        logger.info("Reminder shutdown completed.")

    def schedule_reminders(self):
        """
        Настраивает напоминания на основе событий из расписания.
        """
        logger.info("Scheduling reminders...")
        # Очищаем существующие задачи
        scheduler.remove_all_jobs()
        logger.info("Cleared existing jobs.")

        # Загружаем данные
        self.data = load_data()
        chat_id = self.data.get("chat_id")
        logger.info(f"Loaded chat_id: {chat_id}")

        if not chat_id:
            logger.warning("Chat ID not found in data. Reminders will not be scheduled.")
            return

        # Добавляем задачи для каждого события в расписании
        logger.info(f"Found {len(self.data['schedule'])} events in schedule.")
        for event in self.data["schedule"]:
            time_str = event["time"]  # Формат времени: "ЧЧ:ММ"
            event_name = event["name"]
            logger.info(f"Processing event: {time_str} — {event_name}")

            # Разделяем время на часы и минуты
            try:
                hours, minutes = map(int, time_str.split(":"))
                logger.info(f"Parsed time: {hours}:{minutes}")
            except ValueError as e:
                logger.error(f"Invalid time format for event {time_str} — {event_name}: {e}")
                continue

            # Добавляем задачу в планировщик
            scheduler.add_job(
                self.send_reminder,
                trigger="cron",
                hour=hours,
                minute=minutes,
                args=[chat_id, f"{time_str} — {event_name}"]
            )
            logger.info(f"Scheduled reminder for {time_str} — {event_name}")

    async def send_reminder(self, chat_id: int, message: str) -> None:
        """
        Отправляет напоминание в указанный чат.
        """
        logger.info(f"Attempting to send reminder to chat {chat_id}: {message}")
        try:
            await self.bot.send_message(chat_id=chat_id, text=f"Напоминание: {message}")
            logger.info(f"Reminder sent to chat {chat_id}: {message}")
        except Exception as e:
            logger.error(f"Error sending reminder to chat {chat_id}: {e}")

    def execute(self):
        """
        Выполняет настройку напоминаний.
        """
        logger.info("Executing reminder scheduling...")
        self.schedule_reminders()

    def __call__(self, *args, **kwargs):
        """
        Вызывает execute, если Reminder настроен.
        """
        if not self.setted_up:
            logger.error("Reminder has not been set up!")
            return
        self.execute()