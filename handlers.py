from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from states import AddEventState, RemoveEventState, AddHabitState, AddMoodState
from data_storage import load_data, save_data

from typing import Dict, List, Any

data: Dict[str, Any] = load_data()

menu_keyboard: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="/dobavit_sobytie"), types.KeyboardButton(text="/raspisanue")],
        [types.KeyboardButton(text="/dobavit_privychku"), types.KeyboardButton(text="/privychki")],
        [types.KeyboardButton(text="/dobavit_nastroenie"), types.KeyboardButton(text="/nastroenie")]
    ],
    resize_keyboard=True
)

async def start_handler(message: types.Message) -> None:
    """
    Команда /nachat
    """
    text = (
        "✨ *Привет!* Я твой личный помощник для управления делами и настроением! 🗓️\n\n"
        "Я помогу тебе:\n"
        "📅 Организовать расписание\n"
        "🌱 Следить за привычками\n"
        "😊 Отслеживать настроение\n\n"
        "*Что я умею:*\n"
        "• /dobavit_sobytie — Добавить событие 📌\n"
        "• /raspisanue — Показать расписание 📋\n"
        "• /udalit_sobytie — Удалить событие 🗑️\n"
        "• /dobavit_privychku — Добавить привычку 🌟\n"
        "• /privychki — Показать привычки ✅\n"
        "• /dobavit_nastroenie — Записать настроение 😄\n"
        "• /nastroenie — Показать настроение 📊\n"
        "• /otmena — Отменить текущее действие 🚫\n\n"
        "👇 Используй кнопки ниже, чтобы начать!"
    )
    await message.answer(text, reply_markup=menu_keyboard, parse_mode="Markdown")

async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """
    Команда /otmena. Сбрасывает текущее состояние и возвращает в главное меню
    """
    await state.clear()
    await message.answer("🚫 Действие отменено. Вы вернулись в главное меню.", reply_markup=menu_keyboard)

async def add_event_handler(message: types.Message, state: FSMContext) -> None:
    """
    Команда /dobavit_sobytie. Начинает процесс добавления события
    """
    await state.clear()
    await state.set_state(AddEventState.time)
    await message.answer("Введите время события (например, 09:00):\n(для отмены используйте /otmena)")

async def get_event_time(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает время события
    """
    time: str = message.text
    # Простая проверка формата времени (можно улучшить, если нужно)
    if len(time) == 5 and time[2] == ":" and time[:2].isdigit() and time[3:].isdigit():
        await state.update_data(time=time)
        await state.set_state(AddEventState.name)
        await message.answer("Введите название события:\n(для отмены используйте /otmena)")
    else:
        await message.answer("Пожалуйста, введите время в формате ЧЧ:ММ (например, 09:00).\n(для отмены используйте /otmena)")

async def get_event_name(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает название события
    """
    name: str = message.text.strip()
    if name:
        event_data: Dict[str, str] = await state.get_data()
        time: str = event_data["time"]
        data["schedule"].append({"time": time, "name": name})
        save_data()
        await message.answer(f"Событие добавлено: {time} — {name}", reply_markup=menu_keyboard)
        await state.clear()
    else:
        await message.answer("Название события не может быть пустым. Попробуйте снова!\n(для отмены используйте /otmena)")

async def invalid_input_handler(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает некорректные сообщения в состояниях добавления события
    """
    current_state = await state.get_state()
    if current_state == AddEventState.time.state:
        await message.answer("Пожалуйста, введите время в формате ЧЧ:ММ (например, 09:00).\n(для отмены используйте /otmena)")
    elif current_state == AddEventState.name.state:
        await message.answer("Пожалуйста, введите название события.\n(для отмены используйте /otmena)")

async def schedule_handler(message: types.Message) -> None:
    """
    Команда /raspisanue. Показывает расписание
    """
    if not data["schedule"]:
        await message.answer("Расписание пусто!")
    else:
        text: str = "Ваше расписание:\n"
        for idx, event in enumerate(data["schedule"], start=1):
            text += f"{idx}. {event['time']} — {event['name']}\n"
        await message.answer(text, reply_markup=menu_keyboard)

async def remove_event_handler(message: types.Message, state: FSMContext) -> None:
    """
    Команда /udalit_sobytie. Удаляет событие из расписания
    """
    if not data["schedule"]:
        await message.answer("Расписание пусто! Невозможно удалить событие")
        return

    text: str = "Ваши события:\n"
    for idx, event in enumerate(data["schedule"], start=1):
        text += f"{idx}. {event['time']} — {event['name']}\n"
    text += "\nВведите номер события, которое хотите удалить:"

    await state.set_state(RemoveEventState.event_number)
    await message.answer(text, reply_markup=menu_keyboard)

async def process_remove_event(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает удаление события по номеру
    """
    try:
        event_number: int = int(message.text) - 1
        if 0 <= event_number < len(data["schedule"]):
            removed_event = data["schedule"].pop(event_number)
            save_data()
            await message.answer(f"Событие удалено: {removed_event['time']} — {removed_event['name']}",
                                 reply_markup=menu_keyboard)
        else:
            await message.answer("Неверный номер события. "
                                 "Попробуйте снова!!!")
    except ValueError:
        await message.answer("Пожалуйста!!! "
                             "Введите корректный номер события.")
    finally:
        await state.clear()

async def add_habit_handler(message: types.Message, state: FSMContext) -> None:
    """
    Команда /dobavit_privychku добавления привычки
    """
    await state.set_state(AddHabitState.habit)
    await message.answer("Введите привычку, которую хотите добавить:")

async def process_habit(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает добавление привычки
    """
    habit: str = message.text.strip()
    if habit:
        data["habits"].append(habit)
        save_data()
        await message.answer(f"Привычка '{habit}' добавлена!", reply_markup=menu_keyboard)
        await state.clear()
    else:
        await message.answer("Название привычки не может быть пустым. "
                             "Попробуйте снова!!!")

async def habits_handler(message: types.Message) -> None:
    """
    Команда /privychki список привычек
    """
    if not data["habits"]:
        await message.answer("Привычки отсутствуют!")
    else:
        text: str = "Ваши привычки:\n"
        for habit in data["habits"]:
            text += f"- {habit}\n"
        await message.answer(text, reply_markup=menu_keyboard)

async def add_mood_handler(message: types.Message, state: FSMContext) -> None:
    """
    Команда /dobavit_nastroenie процесс добавления настроения
    """
    await state.set_state(AddMoodState.mood)
    await message.answer("Как вы себя чувствуете сегодня? (например, рад/счастлив/грустно):")

async def record_mood(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает добавление записи настроения
    """
    mood: str = message.text
    data["mood_log"].append(mood)
    save_data()
    await message.answer(f"Ваше настроение записано: {mood}", reply_markup=menu_keyboard)
    await state.clear()

async def mood_handler(message: types.Message) -> None:
    """
    Команда /nastroenie записи о настроении
    """
    if not data["mood_log"]:
        await message.answer("Нет записей о настроении.")
    else:
        text: str = "Ваши записи о настроении:\n"
        for mood in data["mood_log"]:
            text += f"- {mood}\n"
        await message.answer(text, reply_markup=menu_keyboard)

def setup_handlers(dp: Dispatcher) -> None:
    """
    Регистрирует обработчики команд
    """
    dp.message.register(start_handler, Command("nachat"))
    dp.message.register(cancel_handler, Command("otmena"))  # Новый обработчик для /otmena
    dp.message.register(add_event_handler, Command("dobavit_sobytie"))
    dp.message.register(get_event_time, StateFilter(AddEventState.time))
    dp.message.register(get_event_name, StateFilter(AddEventState.name))
    dp.message.register(invalid_input_handler, StateFilter(AddEventState.time, AddEventState.name))  # Новый обработчик для некорректных сообщений
    dp.message.register(schedule_handler, Command("raspisanue"))
    dp.message.register(remove_event_handler, Command("udalit_sobytie"))
    dp.message.register(process_remove_event, StateFilter(RemoveEventState.event_number))
    dp.message.register(add_habit_handler, Command("dobavit_privychku"))
    dp.message.register(process_habit, StateFilter(AddHabitState.habit))
    dp.message.register(habits_handler, Command("privychki"))
    dp.message.register(add_mood_handler, Command("dobavit_nastroenie"))
    dp.message.register(record_mood, StateFilter(AddMoodState.mood))
    dp.message.register(mood_handler, Command("nastroenie"))