from datetime import date


def check_new_day(points, tasks, last_day):
    """
    tasks здесь — количество ОТКРЫТЫХ задач на момент проверки
    (берётся из database.count_tasks). Штраф считается так же,
    как и раньше.
    """
    today = date.today()

    if last_day != today.isoformat():
        days = (today - date.fromisoformat(last_day)).days
        points -= tasks * 100 * days
        last_day = today.isoformat()

    return points, last_day


def add_task_points(points):
    return points + 20


def close_task_points(points):
    return points + 100