from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from config import TOKEN

bot = Bot(TOKEN)
dp = Dispatcher()


class Oper:
    def __init__(self, res, tasks):
        self.res = res
        self.tasks = tasks

    def new_task(self):
        self.res += 20
        self.tasks += 1

    def close_task(self):
        self.res += 100
        if self.tasks > 0:
            self.tasks -= 1

    def new_day(self):
        self.res -= 50 * self.tasks


def load_data():
    try:
        with open("data.txt", "r") as file:
            text = file.read().strip()

            if text:
                res, tasks = map(int, text.split())
                return Oper(res, tasks)
    except FileNotFoundError:
        pass

    return Oper(100, 0)


def save_data():
    with open("data.txt", "w") as file:
        file.write(f"{oper.res} {oper.tasks}")


oper = load_data()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Новый таск")],
        [KeyboardButton(text="✅ Закрыть таск")],
        [KeyboardButton(text="📅 Новый день")],
        [KeyboardButton(text="📊 Статистика")]
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"""Добро пожаловать!

🏆 Очки: {oper.res}
📋 Незакрытые задачи: {oper.tasks}""",
        reply_markup=keyboard
    )


@dp.message(F.text == "➕ Новый таск")
async def new_task(message: Message):
    oper.new_task()
    save_data()

    await message.answer(
        f"Добавлен новый таск.\n\n"
        f"🏆 Очки: {oper.res}\n"
        f"📋 Тасков: {oper.tasks}"
    )


@dp.message(F.text == "✅ Закрыть таск")
async def close_task(message: Message):
    oper.close_task()
    save_data()

    await message.answer(
        f"Таск закрыт.\n\n"
        f"🏆 Очки: {oper.res}\n"
        f"📋 Тасков: {oper.tasks}"
    )


@dp.message(F.text == "📅 Новый день")
async def new_day(message: Message):
    oper.new_day()
    save_data()

    await message.answer(
        f"Наступил новый день.\n\n"
        f"🏆 Очки: {oper.res}\n"
        f"📋 Тасков: {oper.tasks}"
    )


@dp.message(F.text == "📊 Статистика")
async def stats(message: Message):
    await message.answer(
        f"""📊 Статистика

🏆 Очки: {oper.res}
📋 Незакрытые задачи: {oper.tasks}"""
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())