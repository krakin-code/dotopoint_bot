import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import TOKEN
from database import (
    get_user,
    save_user,
    reset_points,
    add_task,
    get_tasks,
    count_tasks,
    delete_task,
)
from operations import (
    check_new_day,
    add_task_points,
    close_task_points,
)

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class TaskForm(StatesGroup):
    waiting_for_task_name = State()


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Новый таск")],
        [KeyboardButton(text="✅ Закрыть таск")],
        [KeyboardButton(text="📅 Новый день")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="⚙️ Настройки")],
    ],
    resize_keyboard=True
)


def load_actual(user_id):
    points, last_day = get_user(user_id)
    tasks = count_tasks(user_id)
    points, last_day = check_new_day(points, tasks, last_day)
    save_user(user_id, points, last_day)
    return points, tasks, last_day


@dp.message(CommandStart())
async def start(message: Message):
    points, tasks, _ = load_actual(message.from_user.id)
    await message.answer(
        f"""Добро пожаловать!
Очки: {points}
Незакрытых задач: {tasks}""",
        reply_markup=keyboard
    )


@dp.message(F.text == "📊 Статистика")
async def stats(message: Message):
    points, tasks, _ = load_actual(message.from_user.id)
    await message.answer(
        f"""📊 Статистика
Очки: {points}
Незакрытых задач: {tasks}"""
    )


@dp.message(F.text == "➕ Новый таск")
async def add_task_start(message: Message, state: FSMContext):
    load_actual(message.from_user.id)
    await message.answer("Введите название задачи:")
    await state.set_state(TaskForm.waiting_for_task_name)


@dp.message(TaskForm.waiting_for_task_name)
async def add_task_finish(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()

    if not text:
        await message.answer("Название не может быть пустым. Введите название задачи:")
        return

    points, _, last_day = load_actual(user_id)
    add_task(user_id, text)
    points = add_task_points(points)
    save_user(user_id, points, last_day)

    await state.clear()
    await message.answer(
        f"""Добавлен новый таск: «{text}»
Очки: {points}"""
    )


@dp.message(F.text == "✅ Закрыть таск")
async def close_task_list(message: Message):
    user_id = message.from_user.id
    load_actual(user_id)
    tasks = get_tasks(user_id)

    if not tasks:
        await message.answer("Открытых задач нет.")
        return

    rows = [
        [InlineKeyboardButton(text=text, callback_data=f"close:{task_id}")]
        for task_id, text in tasks
    ]
    inline_kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer("Выберите задачу для закрытия:", reply_markup=inline_kb)


@dp.callback_query(F.data.startswith("close:"))
async def close_task_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    task_id = int(callback.data.split(":")[1])

    delete_task(task_id)

    points, _, last_day = load_actual(user_id)
    points = close_task_points(points)
    save_user(user_id, points, last_day)

    tasks_left = count_tasks(user_id)

    await callback.message.edit_text(
        f"""Таск закрыт.
Очки: {points}
Незакрытых задач: {tasks_left}"""
    )
    await callback.answer()


@dp.message(F.text == "📅 Новый день")
async def new_day(message: Message):
    points, tasks, _ = load_actual(message.from_user.id)
    await message.answer(
        f"""Если наступил новый день, штраф уже применён автоматически.
Очки: {points}
Незакрытых задач: {tasks}"""
    )


@dp.message(F.text == "⚙️ Настройки")
async def settings_menu(message: Message):
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Сбросить очки", callback_data="reset_points_ask")],
        ]
    )
    await message.answer("Настройки:", reply_markup=inline_kb)


@dp.callback_query(F.data == "reset_points_ask")
async def reset_points_ask(callback: CallbackQuery):
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, сбросить", callback_data="reset_points_confirm"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="reset_points_cancel"),
            ]
        ]
    )
    await callback.message.edit_text(
        "Точно сбросить очки до 0? Это действие нельзя отменить.",
        reply_markup=inline_kb
    )
    await callback.answer()


@dp.callback_query(F.data == "reset_points_confirm")
async def reset_points_confirm(callback: CallbackQuery):
    user_id = callback.from_user.id
    reset_points(user_id)
    await callback.message.edit_text("Очки сброшены до 0.")
    await callback.answer("Готово")


@dp.callback_query(F.data == "reset_points_cancel")
async def reset_points_cancel(callback: CallbackQuery):
    await callback.message.edit_text("Сброс отменён.")
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())