from aiogram.fsm.state import State, StatesGroup

class AddEventState(StatesGroup):
    """
    Состояния для добавления события в расписание
    """
    time: State = State()
    name: State = State()

class RemoveEventState(StatesGroup):
    """
    Состояние для удаления события из расписания.
    """
    event_number: State = State()

class AddHabitState(StatesGroup):
    """
    Состояние для добавления новой привычки.
    """
    habit: State = State()

class AddMoodState(StatesGroup):
    """
    Состояние для записи настроения пользователя.
    """
    mood: State = State()
