import sqlite3
from datetime import date

db = sqlite3.connect("todo.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    points INTEGER,
    last_day TEXT,
    notifications_enabled INTEGER DEFAULT 1
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
            "INSERT INTO users(user_id, points, last_day, notifications_enabled) VALUES(?,?,?,?)",
            (user_id, DEFAULT_POINTS, date.today().isoformat(), 1)
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


def get_notifications_enabled(user_id):
    cursor.execute(
        "SELECT notifications_enabled FROM users WHERE user_id=?",
        (user_id,)
    )
    row = cursor.fetchone()
    if row is None or row[0] is None:
        return True
    return bool(row[0])


def toggle_notifications(user_id):
    new_value = 0 if get_notifications_enabled(user_id) else 1
    cursor.execute(
        "UPDATE users SET notifications_enabled=? WHERE user_id=?",
        (new_value, user_id)
    )
    db.commit()
    return bool(new_value)


def get_users_with_notifications_enabled():
    cursor.execute(
        "SELECT user_id FROM users WHERE notifications_enabled=1"
    )
    return [row[0] for row in cursor.fetchall()]