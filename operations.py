from datetime import date


def check_new_day(points, tasks, last_day):
    today = date.today()

    if last_day != today.isoformat():
        days = (today - date.fromisoformat(last_day)).days
        points -= tasks * 50 * days
        last_day = today.isoformat()

    return points, tasks, last_day


def new_task(points, tasks):
    return points + 20, tasks + 1


def close_task(points, tasks):
    if tasks > 0:
        tasks -= 1
    return points + 100, tasks