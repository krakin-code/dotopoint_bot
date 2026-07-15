import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from config import TOKEN
from database import get_user, save_user
from operations import (
    check_new_day,
    new_task,
    close_task,
)

bot = Bot(TOKEN)
dp = Dispatcher()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Новый таск")],
        [KeyboardButton(text="✅ Закрыть таск")],
        [KeyboardButton(text="📅 Новый день")],
        [KeyboardButton(text="📊 Статистика")]
    ],
    resize_keyboard=True
)


def load_actual(user_id):

    points, tasks, last_day = get_user(user_id)

    points, tasks, last_day = check_new_day(
        points,
        tasks,
        last_day
    )

    save_user(
        user_id,
        points,
        tasks,
        last_day
    )

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
async def add_task(message: Message):

    user_id = message.from_user.id

    points, tasks, last_day = load_actual(user_id)

    points, tasks = new_task(points, tasks)

    save_user(
        user_id,
        points,
        tasks,
        last_day
    )

    await message.answer(
        f"""Добавлен новый таск.

Очки: {points}
Тасков: {tasks}"""
    )


@dp.message(F.text == "✅ Закрыть таск")
async def done_task(message: Message):

    user_id = message.from_user.id

    points, tasks, last_day = load_actual(user_id)

    points, tasks = close_task(points, tasks)

    save_user(
        user_id,
        points,
        tasks,
        last_day
    )

    await message.answer(
        f"""Таск закрыт.

Очки: {points}
Тасков: {tasks}"""
    )


@dp.message(F.text == "📅 Новый день")
async def new_day(message: Message):

    points, tasks, _ = load_actual(message.from_user.id)

    await message.answer(
        f"""Если наступил новый день, штраф уже применён автоматически.

Очки: {points}
Тасков: {tasks}"""
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())