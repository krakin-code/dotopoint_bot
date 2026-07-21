import asyncio
from datetime import datetime, timedelta, time



from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
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
    get_notifications_enabled,
    toggle_notifications,
    get_users_with_notifications_enabled,
)
from operations import (
    check_new_day,
    add_task_points,
    close_task_points,
)

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Фиксированное время рассылки уведомлений
NOTIFY_TIMES = [time(7, 0), time(13, 0), time(19, 0)]


class TaskForm(StatesGroup):
    waiting_for_task_name = State()


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Новый таск")],
        [KeyboardButton(text="✅ Закрыть таск")],
        #[KeyboardButton(text="📅 Новый день")],
        [KeyboardButton(text="📊 Таски\Статистика")],
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


def build_settings_kb(user_id):
    notif_label = (
        "🔔 Уведомления: Вкл"
        if get_notifications_enabled(user_id)
        else "🔕 Уведомления: Выкл"
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Сбросить очки", callback_data="reset_points_ask")],
            [InlineKeyboardButton(text=notif_label, callback_data="notifications_toggle")],
        ]
    )


def build_settings_text(user_id):
    points, _, _ = load_actual(user_id)
    return f"""Настройки:
Твои очки: {points}
Уведомления приходят в 10:00, 16:00, 22:00 по мск"""


@dp.message(CommandStart())
async def start(message: Message):
    points, tasks, _ = load_actual(message.from_user.id)
    await message.answer(
        f"""Добро пожаловать!
Очки: {points}
Незакрытых тасков: {tasks}""",
        reply_markup=keyboard
    )


@dp.message(F.text == "📊 Таски\Статистика")
async def stats(message: Message):
    user_id = message.from_user.id
    points, tasks, _ = load_actual(user_id)

    text = f"""📊 Статистика:
Очки: {points}
Незакрытых тасков: {tasks}"""

    if tasks > 0:
        task_list = get_tasks(user_id)
        task_lines = "\n<b>Таски</b>:\n" + "\n".join(f"• {t}" for _, t in task_list)
        text += f"\n{task_lines}"

    await message.answer(text, parse_mode=ParseMode.HTML)


@dp.message(F.text == "➕ Новый таск")
async def add_task_start(message: Message, state: FSMContext):
    load_actual(message.from_user.id)
    await message.answer("Введите название таска:")
    await state.set_state(TaskForm.waiting_for_task_name)


@dp.message(TaskForm.waiting_for_task_name)
async def add_task_finish(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()

    if not text:
        await message.answer("Название не может быть пустым. Введите название таска:")
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
        await message.answer("Открытых тасков нет.")
        return

    rows = [
        [InlineKeyboardButton(text=text, callback_data=f"close:{task_id}")]
        for task_id, text in tasks
    ]
    inline_kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer("Выберите таск для закрытия:", reply_markup=inline_kb)


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
Незакрытых тасков: {tasks_left}"""
    )
    await callback.answer()


# @dp.message(F.text == "📅 Новый день")
# async def new_day(message: Message):
#     points, tasks, _ = load_actual(message.from_user.id)
#     await message.answer(
#         f"""Если наступил новый день, штраф уже применён автоматически.
# Очки: {points}
# Незакрытых задач: {tasks}"""
#     )


@dp.message(F.text == "⚙️ Настройки")
async def settings_menu(message: Message):
    user_id = message.from_user.id
    await message.answer(
        build_settings_text(user_id),
        reply_markup=build_settings_kb(user_id)
    )


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
    await callback.message.edit_text(
        f"Очки сброшены до 0.\n\n{build_settings_text(user_id)}",
        reply_markup=build_settings_kb(user_id)
    )
    await callback.answer("Готово")


@dp.callback_query(F.data == "reset_points_cancel")
async def reset_points_cancel(callback: CallbackQuery):
    await callback.message.edit_text(
        build_settings_text(callback.from_user.id),
        reply_markup=build_settings_kb(callback.from_user.id)
    )
    await callback.answer()


@dp.callback_query(F.data == "notifications_toggle")
async def notifications_toggle_cb(callback: CallbackQuery):
    toggle_notifications(callback.from_user.id)
    await callback.message.edit_reply_markup(
        reply_markup=build_settings_kb(callback.from_user.id)
    )
    await callback.answer("Обновлено")


async def send_notifications():
    for user_id in get_users_with_notifications_enabled():
        tasks = count_tasks(user_id)

        if tasks == 0:
            continue

        try:
            await bot.send_message(
                user_id,
                f"⏰У тебя {tasks} невыполненных тасков."
            )
        except Exception:
            # пользователь заблокировал бота, чат недоступен и т.п.
            pass


async def notifier_loop():
    while True:
        now = datetime.now()

        candidates_today = [datetime.combine(now.date(), t) for t in NOTIFY_TIMES]
        future_today = [c for c in candidates_today if c > now]

        if future_today:
            next_time = min(future_today)
        else:
            next_time = datetime.combine(now.date() + timedelta(days=1), NOTIFY_TIMES[0])

        await asyncio.sleep((next_time - now).total_seconds())
        await send_notifications()


async def main():
    asyncio.create_task(notifier_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())