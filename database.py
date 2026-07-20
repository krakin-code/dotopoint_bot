import sqlite3
from datetime import date

db = sqlite3.connect("todo.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    points INTEGER,
    last_day TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT
)
""")

db.commit()

DEFAULT_POINTS = 100


def get_user(user_id):

    cursor.execute(
        "SELECT points,last_day FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:

        cursor.execute(
            "INSERT INTO users VALUES(?,?,?)",
            (user_id, DEFAULT_POINTS, date.today().isoformat())
        )

        db.commit()

        return DEFAULT_POINTS, date.today().isoformat()

    return user


def save_user(user_id, points, last_day):

    cursor.execute("""
    UPDATE users
    SET points=?,last_day=?
    WHERE user_id=?
    """, (points, last_day, user_id))

    db.commit()


def reset_points(user_id):
    """Обнуляет очки пользователя. Список задач не трогает."""
    cursor.execute(
        "UPDATE users SET points=0 WHERE user_id=?",
        (user_id,)
    )
    db.commit()


def add_task(user_id, text):
    cursor.execute(
        "INSERT INTO tasks(user_id, text) VALUES(?,?)",
        (user_id, text)
    )
    db.commit()


def get_tasks(user_id):
    """Возвращает список открытых задач: [(task_id, text), ...]"""
    cursor.execute(
        "SELECT task_id, text FROM tasks WHERE user_id=?",
        (user_id,)
    )
    return cursor.fetchall()


def count_tasks(user_id):
    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE user_id=?",
        (user_id,)
    )
    return cursor.fetchone()[0]


def delete_task(task_id):
    cursor.execute(
        "DELETE FROM tasks WHERE task_id=?",
        (task_id,)
    )
    db.commit()