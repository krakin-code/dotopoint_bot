import sqlite3
from datetime import date

db = sqlite3.connect("todo.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    points INTEGER,
    tasks INTEGER,
    last_day TEXT
)
""")

db.commit()


def get_user(user_id):

    cursor.execute(
        "SELECT points,tasks,last_day FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:

        cursor.execute(
            "INSERT INTO users VALUES(?,?,?,?)",
            (user_id,100,0,date.today().isoformat())
        )

        db.commit()

        return 100,0,date.today().isoformat()

    return user


def save_user(user_id,points,tasks,last_day):

    cursor.execute("""
    UPDATE users
    SET points=?,tasks=?,last_day=?
    WHERE user_id=?
    """,(points,tasks,last_day,user_id))

    db.commit()