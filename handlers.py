from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from states import AddEventState, RemoveEventState, AddHabitState, AddMoodState
from data_storage import load_data, save_data

from typing import Dict, List, Any

data: Dict[str, Any] = load_data()

menu_keyboard: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="/add_event"), types.KeyboardButton(text="/schedule")],
        [types.KeyboardButton(text="/add_habit"), types.KeyboardButton(text="/habits")],
        [types.KeyboardButton(text="/add_mood"), types.KeyboardButton(text="/mood")]
    ],
    resize_keyboard=True
)



async def start_handler(message: types.Message) -> None:
    """
    Команда /start
    """
    text = (
        "Привет! Я помогу тебе управлять расписанием, привычками и настроением.\n\n"
        "Используйте кнопки ниже для взаимодействия"
    )
    await message.answer(text, reply_markup=menu_keyboard)


async def add_event_handler(message: types.Message, state: FSMContext) -> None:
    """
    Команда /add_event. Начинает процесс добавления события
    """
    await state.clear()
    await state.set_state(AddEventState.time)
    await message.answer("Введите время события (например, 09:00):")


async def get_event_time(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает время события
    """
    time: str = message.text
    await state.update_data(time=time)
    await state.set_state(AddEventState.name)
    await message.answer("Введите название события:")


async def get_event_name(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает название события
    """
    name: str = message.text
    event_data: Dict[str, str] = await state.get_data()
    time: str = event_data["time"]

    data["schedule"].append({"time": time, "name": name})
    save_data()

    await message.answer(f"Событие добавлено: {time} — {name}", reply_markup=menu_keyboard)
    await state.clear()


async def schedule_handler(message: types.Message) -> None:
    """
    Команда /schedule. Показывает расписание
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
    Команды /remove_event. Удаляет событие из расписания
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
    Команды /add_habit добавления привычки
    """
    await state.set_state(AddHabitState.habit)
    await message.answer("Введите привычку, которую хотите добавить:")


async def process_habit(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает добавление привычкы
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
    Команда /habits список привычек
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
    Команда /add_mood процесс добавления настроения
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
    Команды /mood записи о настроении
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
    Обработчики команд
    """
    dp.message.register(start_handler, Command("start"))
    dp.message.register(add_event_handler, Command("add_event"))
    dp.message.register(get_event_time, StateFilter(AddEventState.time))
    dp.message.register(get_event_name, StateFilter(AddEventState.name))
    dp.message.register(schedule_handler, Command("schedule"))
    dp.message.register(remove_event_handler, Command("remove_event"))
    dp.message.register(process_remove_event, StateFilter(RemoveEventState.event_number))
    dp.message.register(add_habit_handler, Command("add_habit"))
    dp.message.register(process_habit, StateFilter(AddHabitState.habit))
    dp.message.register(habits_handler, Command("habits"))
    dp.message.register(add_mood_handler, Command("add_mood"))
    dp.message.register(record_mood, StateFilter(AddMoodState.mood))
    dp.message.register(mood_handler, Command("mood"))
