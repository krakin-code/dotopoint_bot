#
# class Oper:
#     def __init__(self, res, tasks):
#         self.res = res
#         self.tasks = tasks
#     def new_task(self):
#         self.res += 20
#         self.tasks += 1
#         return self.res, self.tasks
#     def close_task(self):
#         self.res += 100
#         self.tasks -= 1
#         return self.res, self.tasks
#     def new_day(self):
#         self.res -= 50 * self.tasks
#         return self.res
#
#
# def main():
#     try:
#         file = open('todo_res.txt', 'r+')
#         file_data = file.read()
#
#         if len(file_data) > 0:
#             act_day = file_data.split('\n')[-1]
#             res, tasks = act_day.split(' ')
#
#
#         else:
#             print('К сожалению ваш файл с данными пуст. Давайте восполним пробелы.')
#             res = input('Введите начально количество очков (рекомендуем - 100):')
#             tasks = input('Введите количество незакрытых тасков:')
#             act_day = res + ' ' + tasks
#             file.write(act_day)
#
#
#
#     except FileNotFoundError:
#         res = input('Упс! Похоже вы в первый раз запускаете программу.\nНужно ввести начальное значение очков:')
#         tasks = input('Ещё нам нужно ваше количество незакрытых тасков:')
#         with open('todo_res.txt', 'w') as file:
#             act_day = res + ' ' + tasks
#             file.write(act_day)
#
#     res = int(res)
#     tasks = int(tasks)
#     start_day_res = res
#     start_day_tasks = tasks
#     point_operation = Oper(res, tasks)
#
#     while True:
#         print(f'Ваши очки: {res} \nНезакрытые таски: {tasks}\n')
#         do = int(input('Выберите действие:\n1 - новый таск\n2 - закрыть таск\n3 - новый день\n4 - выход\n'))
#         if do == 1:
#             res, tasks = point_operation.new_task()
#         if do == 2:
#             res, tasks = point_operation.close_task()
#         if do == 3:
#             res = point_operation.new_day()
#         if do == 4:
#
#             file.write('\n')
#             file.write(str(res) + ' ' + str(tasks))
#             print(f'За сегодня вы получили {res - start_day_res} очков и закрыли {tasks - start_day_tasks} задач')
#             exit()
#         print('\n')
#
#
#
# if __name__ == '__main__':
#     main()

from aiogram import Bot, Dispatcher
import asyncio

bot = Bot("8789607041:AAFsJJ0ilmZMHa4m-hkmJjpvVqYM1Qas52w")
dp = Dispatcher()

@dp.message()
async def echo(message):
    await message.answer(message.text)

async def main():
    await dp.start_polling(bot)

asyncio.run(main())