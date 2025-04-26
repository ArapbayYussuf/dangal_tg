from aiogram import types, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states import AddEventState, RemoveEventState, AddHabitState, AddMoodState
from data_storage import load_data, save_data
from reminders import Reminder
from typing import Dict, Any
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

data: Dict[str, Any] = load_data()

# Инлайн-клавиатура с эмодзи
menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Событие➕", callback_data="add_event"),
        InlineKeyboardButton(text="Расписание📋", callback_data="show_schedule"),
        InlineKeyboardButton(text="Удалить🗑️", callback_data="remove_event")
    ],
    [
        InlineKeyboardButton(text="Добавить привычку🌟", callback_data="add_habit"),
        InlineKeyboardButton(text="Привычка✅", callback_data="show_habits")
    ],
    [
        InlineKeyboardButton(text="Добавить настроение😊", callback_data="add_mood"),
        InlineKeyboardButton(text="Настроение📊", callback_data="show_mood")
    ]
])


async def start_handler(message: types.Message, reminder: Reminder) -> None:
    """
    Команда /start
    """
    global data
    logger.info(f"Received /start command from chat_id: {message.chat.id}")
    data["chat_id"] = message.chat.id  # Сохраняем chat_id
    save_data()
    logger.info(f"Saved chat_id to data.json: {data['chat_id']}")

    # Обновляем напоминания
    reminder.execute()
    logger.info("Called reminder.execute() after /start")

    text = (
        "Привет! Я *Напомни мне* — твой помощник для управления делами и настроением 📅.\n\n"
        "Я помогу с расписанием, привычками и настроением.\n\n"
        "Нажми /start или /help!"
    )
    await message.answer(text, reply_markup=menu_keyboard, parse_mode="Markdown")


async def help_handler(message: types.Message) -> None:
    """
    Команда /help
    """
    logger.info("Received /help command")
    text = (
        "Я *Напомни мне*, и я умею:\n"
        "- Добавить событие в расписание: /dobavit_sobytie\n"
        "- Показать расписание: /raspisanue\n"
        "- Удалить событие: /udalit_sobytie\n"
        "- Добавить привычку: /dobavit_privychku\n"
        "- Показать привычки: /privychki\n"
        "- Записать настроение: /dobavit_nastroenie\n"
        "- Показать настроение: /nastroenie\n"
        "- Отменить действие: /otmena\n\n"
        "Нажми /start, чтобы вернуться в меню!"
    )
    await message.answer(text, parse_mode="Markdown")


async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """
    Команда /otmena. Сбрасывает текущее состояние и возвращает в главное меню
    """
    logger.info("Received /otmena command")
    await state.clear()
    await message.answer("Действие отменено. Вы вернулись в главное меню.", reply_markup=menu_keyboard)


async def add_event_handler(message: types.Message, state: FSMContext, reminder: Reminder) -> None:
    """
    Команда /dobavit_sobytie. Начинает процесс добавления события
    """
    logger.info("Received /dobavit_sobytie command")
    await state.clear()
    await state.set_state(AddEventState.time)
    await message.answer("Введите время события (например, 09:00):\n(для отмены используйте /otmena)")


async def callback_add_event(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает нажатие на инлайн-кнопку для добавления события
    """
    logger.info("Received callback for add_event")
    await state.clear()
    await state.set_state(AddEventState.time)
    await callback_query.message.answer("Введите время события (например, 09:00):\n(для отмены используйте /otmena)")
    await callback_query.answer()


async def get_event_time(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает время события
    """
    logger.info(f"Received event time: {message.text}")
    time: str = message.text
    if len(time) == 5 and time[2] == ":" and time[:2].isdigit() and time[3:].isdigit():
        await state.update_data(time=time)
        await state.set_state(AddEventState.name)
        await message.answer("Введите название события:\n(для отмены используйте /otmena)")
    else:
        await message.answer(
            "❌ Неверный формат времени! Введите в формате ЧЧ:ММ (например, 09:00).\n(для отмены используйте /otmena)")


async def get_event_name(message: types.Message, state: FSMContext, reminder: Reminder) -> None:
    """
    Обрабатывает название события
    """
    logger.info(f"Received event name: {message.text}")
    name: str = message.text.strip()
    if name:
        event_data: Dict[str, str] = await state.get_data()
        time: str = event_data["time"]
        data["schedule"].append({"time": time, "name": name})
        save_data()
        # Обновляем напоминания после добавления события
        reminder.execute()
        logger.info("Called reminder.execute() after adding event")
        await message.answer(f"✅ Событие добавлено: {time} — {name}", reply_markup=menu_keyboard)
        await state.clear()
    else:
        await message.answer(
            "❌ Название события не может быть пустым! Попробуйте снова.\n(для отмены используйте /otmena)")


async def invalid_input_handler(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает некорректные сообщения в состояниях добавления события
    """
    logger.info("Received invalid input in event state")
    current_state = await state.get_state()
    if current_state == AddEventState.time.state:
        await message.answer(
            "❌ Неверный формат времени! Введите в формате ЧЧ:ММ (например, 09:00).\n(для отмены используйте /otmena)")
    elif current_state == AddEventState.name.state:
        await message.answer("❌ Введите название события!\n(для отмены используйте /otmena)")


async def schedule_handler(message: types.Message) -> None:
    """
    Команда /raspisanue. Показывает расписание
    """
    logger.info("Received /raspisanue command")
    if not data["schedule"]:
        await message.answer("Расписание пусто!")
    else:
        text: str = "Ваше расписание:\n"
        for idx, event in enumerate(data["schedule"], start=1):
            text += f"{idx}. {event['time']} — {event['name']}\n"
        await message.answer(text, reply_markup=menu_keyboard)


async def callback_show_schedule(callback_query: types.CallbackQuery) -> None:
    """
    Обрабатывает нажатие на инлайн-кнопку для показа расписания
    """
    logger.info("Received callback for show_schedule")
    if not data["schedule"]:
        await callback_query.message.answer("Расписание пусто!")
    else:
        text: str = "Ваше расписание:\n"
        for idx, event in enumerate(data["schedule"], start=1):
            text += f"{idx}. {event['time']} — {event['name']}\n"
        await callback_query.message.answer(text, reply_markup=menu_keyboard)
    await callback_query.answer()


async def remove_event_handler(message: types.Message, state: FSMContext, reminder: Reminder) -> None:
    """
    Команда /udalit_sobytie. Удаляет событие из расписания
    """
    logger.info("Received /udalit_sobytie command")
    if not data["schedule"]:
        await message.answer("Расписание пусто! Невозможно удалить событие.")
        return

    text: str = "Ваши события:\n"
    for idx, event in enumerate(data["schedule"], start=1):
        text += f"{idx}. {event['time']} — {event['name']}\n"
    text += "\nВыберите номер события для удаления:"

    # Создаем инлайн-клавиатуру для удаления
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for idx in range(len(data["schedule"])):
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=f"🗑️ {idx + 1}", callback_data=f"delete_event_{idx}")
        ])

    await state.set_state(RemoveEventState.event_number)
    await message.answer(text, reply_markup=keyboard)


async def callback_remove_event(callback_query: types.CallbackQuery, state: FSMContext, reminder: Reminder) -> None:
    """
    Обрабатывает нажатие на инлайн-кнопку для удаления события
    """
    logger.info("Received callback for remove_event")
    if not data["schedule"]:
        await callback_query.message.answer("Расписание пусто! Невозможно удалить событие.")
        await callback_query.answer()
        return

    text: str = "Ваши события:\n"
    for idx, event in enumerate(data["schedule"], start=1):
        text += f"{idx}. {event['time']} — {event['name']}\n"
    text += "\nВыберите номер события для удаления:"

    # Создаем инлайн-клавиатуру для удаления
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for idx in range(len(data["schedule"])):
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=f"🗑️ {idx + 1}", callback_data=f"delete_event_{idx}")
        ])

    await state.set_state(RemoveEventState.event_number)
    await callback_query.message.answer(text, reply_markup=keyboard)
    await callback_query.answer()


async def process_remove_event_callback(callback_query: types.CallbackQuery, state: FSMContext,
                                        reminder: Reminder) -> None:
    """
    Обрабатывает удаление события по нажатию на инлайн-кнопку
    """
    logger.info(f"Received callback for delete_event: {callback_query.data}")
    event_number = int(callback_query.data.split("_")[-1])
    if 0 <= event_number < len(data["schedule"]):
        removed_event = data["schedule"].pop(event_number)
        save_data()
        # Обновляем напоминания после удаления события
        reminder.execute()
        logger.info("Called reminder.execute() after removing event")
        await callback_query.message.answer(
            f"✅ Событие удалено: {removed_event['time']} — {removed_event['name']}",
            reply_markup=menu_keyboard
        )
        await callback_query.message.delete()  # Удаляем сообщение с клавиатурой
    else:
        await callback_query.message.answer("❌ Неверный номер события! Попробуйте снова.")
    await state.clear()
    await callback_query.answer()


async def process_remove_event_text(message: types.Message, state: FSMContext, reminder: Reminder) -> None:
    """
    Обрабатывает удаление события по текстовому вводу номера
    """
    logger.info(f"Received event number for removal: {message.text}")
    try:
        event_number: int = int(message.text) - 1
        if 0 <= event_number < len(data["schedule"]):
            removed_event = data["schedule"].pop(event_number)
            save_data()
            # Обновляем напоминания после удаления события
            reminder.execute()
            logger.info("Called reminder.execute() after removing event via text")
            await message.answer(
                f"✅ Событие удалено: {removed_event['time']} — {removed_event['name']}",
                reply_markup=menu_keyboard
            )
        else:
            await message.answer("❌ Неверный номер события! Попробуйте снова.")
    except ValueError:
        await message.answer("❌ Введите корректный номер события!")
    finally:
        await state.clear()


async def add_habit_handler(message: types.Message, state: FSMContext) -> None:
    """
    Команда /dobavit_privychku добавления привычки
    """
    logger.info("Received /dobavit_privychku command")
    await state.set_state(AddHabitState.habit)
    await message.answer("Введите привычку, которую хотите добавить:")


async def callback_add_habit(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает нажатие на инлайн-кнопку для добавления привычки
    """
    logger.info("Received callback for add_habit")
    await state.set_state(AddHabitState.habit)
    await callback_query.message.answer("Введите привычку, которую хотите добавить:")
    await callback_query.answer()


async def process_habit(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает добавление привычки
    """
    logger.info(f"Received habit: {message.text}")
    habit: str = message.text.strip()
    if habit:
        data["habits"].append(habit)
        save_data()
        await message.answer(f"✅ Привычка '{habit}' добавлена!", reply_markup=menu_keyboard)
        await state.clear()
    else:
        await message.answer("❌ Название привычки не может быть пустым! Попробуйте снова.")


async def habits_handler(message: types.Message) -> None:
    """
    Команда /privychki список привычек
    """
    logger.info("Received /privychki command")
    if not data["habits"]:
        await message.answer("Привычки отсутствуют!")
    else:
        text: str = "Ваши привычки:\n"
        for habit in data["habits"]:
            text += f"- {habit}\n"
        await message.answer(text, reply_markup=menu_keyboard)


async def callback_show_habits(callback_query: types.CallbackQuery) -> None:
    """
    Обрабатывает нажатие на инлайн-кнопку для показа привычек
    """
    logger.info("Received callback for show_habits")
    if not data["habits"]:
        await callback_query.message.answer("Привычки отсутствуют!")
    else:
        text: str = "Ваши привычки:\n"
        for habit in data["habits"]:
            text += f"- {habit}\n"
        await callback_query.message.answer(text, reply_markup=menu_keyboard)
    await callback_query.answer()


async def add_mood_handler(message: types.Message, state: FSMContext) -> None:
    """
    Команда /dobavit_nastroenie процесс добавления настроения
    """
    logger.info("Received /dobavit_nastroenie command")
    await state.set_state(AddMoodState.mood)
    await message.answer("Как вы себя чувствуете сегодня? (например, рад/счастлив/грустно):")


async def callback_add_mood(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает нажатие на инлайн-кнопку для добавления настроения
    """
    logger.info("Received callback for add_mood")
    await state.set_state(AddMoodState.mood)
    await callback_query.message.answer("Как вы себя чувствуете сегодня? (например, рад/счастлив/грустно):")
    await callback_query.answer()


async def record_mood(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает добавление записи настроения
    """
    logger.info(f"Received mood: {message.text}")
    mood: str = message.text
    data["mood_log"].append(mood)
    save_data()
    await message.answer(f"✅ Ваше настроение записано: {mood}", reply_markup=menu_keyboard)
    await state.clear()


async def mood_handler(message: types.Message) -> None:
    """
    Команда /nastroenie записи о настроении
    """
    logger.info("Received /nastroenie command")
    if not data["mood_log"]:
        await message.answer("Нет записей о настроении.")
    else:
        text: str = "Ваши записи о настроении:\n"
        for mood in data["mood_log"]:
            text += f"- {mood}\n"
        await message.answer(text, reply_markup=menu_keyboard)


async def callback_show_mood(callback_query: types.CallbackQuery) -> None:
    """
    Обрабатывает нажатие на инлайн-кнопку для показа настроения
    """
    logger.info("Received callback for show_mood")
    if not data["mood_log"]:
        await callback_query.message.answer("Нет записей о настроении.")
    else:
        text: str = "Ваши записи о настроении:\n"
        for mood in data["mood_log"]:
            text += f"- {mood}\n"
        await callback_query.message.answer(text, reply_markup=menu_keyboard)
    await callback_query.answer()


def setup_handlers(dp: Dispatcher, reminder: Reminder) -> None:
    """
    Регистрирует обработчики команд
    """

    # Команда /start
    async def start_wrapper(message: types.Message):
        await start_handler(message, reminder)

    dp.message.register(start_wrapper, Command("start"))

    # Команда /help
    dp.message.register(help_handler, Command("help"))

    # Команда /otmena
    dp.message.register(cancel_handler, Command("otmena"))

    # Команда /dobavit_sobytie
    async def add_event_wrapper(message: types.Message, state: FSMContext):
        await add_event_handler(message, state, reminder)

    dp.message.register(add_event_wrapper, Command("dobavit_sobytie"))

    # Инлайн-кнопка добавления события
    dp.callback_query.register(callback_add_event, lambda c: c.data == "add_event")

    # Обработка времени события
    dp.message.register(get_event_time, StateFilter(AddEventState.time))

    # Обработка названия события
    async def get_event_name_wrapper(message: types.Message, state: FSMContext):
        await get_event_name(message, state, reminder)

    dp.message.register(get_event_name_wrapper, StateFilter(AddEventState.name))

    # Обработка некорректного ввода в состояниях добавления события
    dp.message.register(invalid_input_handler, StateFilter(AddEventState.time, AddEventState.name))

    # Команда /raspisanue
    dp.message.register(schedule_handler, Command("raspisanue"))

    # Инлайн-кнопка показа расписания
    dp.callback_query.register(callback_show_schedule, lambda c: c.data == "show_schedule")

    # Команда /udalit_sobytie
    async def remove_event_wrapper(message: types.Message, state: FSMContext):
        await remove_event_handler(message, state, reminder)

    dp.message.register(remove_event_wrapper, Command("udalit_sobytie"))

    # Инлайн-кнопка удаления события
    async def callback_remove_event_wrapper(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_remove_event(callback_query, state, reminder)

    dp.callback_query.register(callback_remove_event_wrapper, lambda c: c.data == "remove_event")

    # Обработка удаления события по инлайн-кнопке
    async def process_remove_event_callback_wrapper(callback_query: types.CallbackQuery, state: FSMContext):
        await process_remove_event_callback(callback_query, state, reminder)

    dp.callback_query.register(process_remove_event_callback_wrapper, lambda c: c.data.startswith("delete_event_"))

    # Обработка удаления события по тексту
    async def process_remove_event_text_wrapper(message: types.Message, state: FSMContext):
        await process_remove_event_text(message, state, reminder)

    dp.message.register(process_remove_event_text_wrapper, StateFilter(RemoveEventState.event_number))

    # Команда /dobavit_privychku
    dp.message.register(add_habit_handler, Command("dobavit_privychku"))

    # Инлайн-кнопка добавления привычки
    dp.callback_query.register(callback_add_habit, lambda c: c.data == "add_habit")

    # Обработка добавления привычки
    dp.message.register(process_habit, StateFilter(AddHabitState.habit))

    # Команда /privychki
    dp.message.register(habits_handler, Command("privychki"))

    # Инлайн-кнопка показа привычек
    dp.callback_query.register(callback_show_habits, lambda c: c.data == "show_habits")

    # Команда /dobavit_nastroenie
    dp.message.register(add_mood_handler, Command("dobavit_nastroenie"))

    # Инлайн-кнопка добавления настроения
    dp.callback_query.register(callback_add_mood, lambda c: c.data == "add_mood")

    # Обработка добавления настроения
    dp.message.register(record_mood, StateFilter(AddMoodState.mood))

    # Команда /nastroenie
    dp.message.register(mood_handler, Command("nastroenie"))

    # Инлайн-кнопка показа настроения
    dp.callback_query.register(callback_show_mood, lambda c: c.data == "show_mood")