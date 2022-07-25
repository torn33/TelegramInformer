# -*- coding: utf-8 -*-
import datetime
import pandas as pd
from aiogram import Bot, Dispatcher, executor, types
import asyncio
import aioschedule
try:
    file =open ("token.txt","r") #считываем токен из файла
    token=file.read()
    bot = Bot(token=token)  # тут хранится токен
except:
    print("файл с токеном не обнаружен")
    exit()
now = datetime.datetime.now()
bot = Bot(token=token)  # тут хранится токен
dp = Dispatcher(bot)

reg_mode = False
flag_infuser = False  # переменная для хранения состояния наличия информации в файле расписания
flag_infpass = False  # переменная для хранения состояния наличия информации в файле расписания
user_login = ""


def report_add(user_name,user_id):
    report = "Пользователь " + user_name + " c ID " + str(
        user_id) + " запрашивал информацию о ВКС в " + str(now)
    print(report)
    f = open('report.txt', 'a')
    f.write(report + "\n")
    f.close()


@dp.message_handler(
    commands="start")  # обработчик команды "start" , при написании команды /start создаются кнопки и отправляются сообщения
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Кто сегодня?", "Кто завтра?", "Все расписание"]
    keyboard.add(*buttons)
    await message.answer("Диспетчер, слушаю... 📞", reply_markup=keyboard)


@dp.message_handler(commands="help")  # обработчик команды "help", краткая инструкция о командах
async def cmd_help(message: types.Message):
    await message.answer("Команда /start для начала работы с ботом\n Команда /date чтобы сверить дату и время с "
                         "ботом\n Команда /id чтобы узнать свой ID\n Команда /reg для регистрации\n Команда /exitreg для выхода из режима регистрации\n")


@dp.message_handler(commands="date")  # обработчик команды "date", выводит текущую дату на сервере
async def cmd_date(message: types.Message):
    await message.answer(now)


@dp.message_handler(commands="id")  # обработчик команды "id", выводит id Telegram
async def cmd_id(message: types.Message):
    await message.answer(message.from_user.id)


@dp.message_handler(commands="reg")  # обработчик команды "reg", запускает процесс регистрации пользователя
async def cmd_reg(message: types.Message):
    global reg_mode
    reg_mode = True
    await message.answer("Приветствую! Режим регистрации включен (для выхода /exitreg)\n")
    await message.answer("Введите в качестве логина инициалы в формате ФИО\n")


@dp.message_handler(commands="exitreg")  # обработчик команды "exitreg", выход из режима регистраци
async def cmd_exitreg(message: types.Message):
    global reg_mode
    reg_mode = False
    await message.answer("Режим регистрации выключен\n")


@dp.message_handler(lambda message: message.text == "Кто сегодня?") #обработчик кнопки
async def today(message: types.Message):
    flag_idfount = False
    users = pd.read_csv('Users.csv', delimiter=';')
    for ind in users.index:
        if users['tg_id'][ind] == message.from_user.id:
            flag_idfount = True
            await message.answer("Сейчас посмотрим...")
            flag_inf = False  # переменная для хранения состояния наличия информации в файле расписания
            try:
                switches = pd.read_csv('VKS.csv', delimiter=';')
                today = now.strftime("%d.%m.%Y")
                for ind in switches.index:
                    if switches['date'][ind] == str(today):
                        answer = "Сегодня " + str(today) + " приходит " + switches['name'][ind]
                        await message.answer(answer)
                        report_add(message.from_user.first_name,message.from_user.id)
                        flag_inf = True
                if flag_inf == False:
                    await message.answer("Информация не найдена! ¯\_(ツ)_/¯")

            except FileNotFoundError:
                await message.answer("Я потерял свой журнал, пока не могу помочь 😕")
                print('Файл с расписанием не обнаружен!')
            break

    if flag_idfount==False:
        await message.answer("Пользователь не зарегистрирован, доступ запрещен")




@dp.message_handler(lambda message: message.text == "Все расписание")
async def all(message: types.Message):
    answer = ""
    flag_idfount = False
    users = pd.read_csv('Users.csv', delimiter=';')
    for ind in users.index:
        if users['tg_id'][ind] == message.from_user.id:
            flag_idfount = True
            await message.answer("Выкатываю...")
            try:
                switches = pd.read_csv('VKS.csv', delimiter=';')
                for ind in switches.index:
                    answerbufer = switches['date'][ind] + " - " + switches['name'][ind] + "\n"
                    answer += answerbufer
                await message.answer(answer)
                report_add(message.from_user.first_name, message.from_user.id)

            except FileNotFoundError:
                await message.answer("Я потерял свой журнал, пока не могу помочь 😕")
                print('Файл с расписанием не обнаружен!')
    if flag_idfount == False:
        await message.answer("Пользователь не зарегистрирован, доступ запрещен")


@dp.message_handler(lambda message: message.text == "Кто завтра?")
async def tomorrow(message: types.Message):
    flag_inf = False  # переменная для хранения состояния наличия информации в файле расписания
    flag_idfount = False
    users = pd.read_csv('Users.csv', delimiter=';')
    for ind in users.index:
        if users['tg_id'][ind] == message.from_user.id:
            flag_idfount = True
            await message.answer("Сейчас посмотрим...")
            try:
                switches = pd.read_csv('VKS.csv', delimiter=';')
                tomorrowdate = datetime.date.today() + datetime.timedelta(days=1)
                for ind in switches.index:
                    if switches['date'][ind] == str(tomorrowdate.strftime("%d.%m.%Y")):
                        answer = "Завтра " + str(tomorrowdate.strftime("%d.%m.%Y")) + " приходит " + switches['name'][ind]
                        await message.answer(answer)
                        report_add(message.from_user.first_name, message.from_user.id)
                        flag_inf = True
                if (flag_inf == False):
                    await message.answer("Информация не найдена! ¯\_(ツ)_/¯")

            except FileNotFoundError:
                await message.answer("Я потерял свой журнал, пока не могу помочь 😕")
                print('Файл с расписанием не обнаружен!')

    if flag_idfount == False:
        await message.answer("Пользователь не зарегистрирован, доступ запрещен")



@dp.message_handler()
async def chat(message: types.Message):
    global reg_mode
    if not reg_mode:

        if (
                message.text.lower() == "иди на хуй" or message.text == "иди нахуй" or message.text == "Диспетчер иди нахуй!" or message.text == "Диспетчер иди нахуй"):
            await message.answer(
                "Ублюдок, мать твою, а ну иди сюда, говно собачье, решил ко мне лезть? Ты, засранец вонючий, мать твою, а? Ну иди сюда, попробуй меня трахнуть, я тебя сам трахну, ублюдок, онанист чертов, будь ты проклят, иди идиот, трахать тебя и всю семью, говно собачье, жлоб вонючий, дерьмо, сука, падла, иди сюда, мерзавец, негодяй, гад, иди сюда, ты — говно, жопа!")
        if (message.text.lower() == "спасибо"):
            await message.answer("😎")
        else:
            await message.answer("Добрый вечер, я Диспетчер! Не понял,  жми /start!")
    if reg_mode:
        global user_login
        global flag_infuser
        global flag_infpass
        try:

            switches = pd.read_csv('Users.csv', delimiter=';')
            for ind in switches.index:
                if switches['login'][ind].upper() == message.text.upper() and flag_infuser != True:
                    await message.answer("Привет " + switches['login'][ind] + " введи пароль")
                    user_login = switches['login'][ind]
                    flag_infuser = True

            if flag_infuser != True:
                await message.answer("Такой пользователь не найден!¯\_(ツ)_/¯")

        except FileNotFoundError:
            await message.answer("Регистрация не возможна в данный момент😕")
            print('Файл с пользователями не обнаружен!')

        if flag_infuser == True and flag_infpass == False:
            try:

                switches = pd.read_csv('Users.csv', delimiter=';')
                for ind in switches.index:

                    if switches['pass'][ind] == message.text and switches['login'][ind]==user_login:
                        flag_infpass = True

                    if flag_infuser == True and flag_infpass == True :
                        switches.loc[ind,'tg_id'] = str(message.from_user.id)
                        switches.to_csv("Users.csv",sep=';', index=False, encoding='utf-8-sig')
                        report = "Telegram ID " + str(message.from_user.id) + " привязан к инициалам " + user_login
                        await message.answer(report)
                        flag_infuser=False
                        flag_infpass=False

                        reg_mode=False
                        print(report)
                        f = open('report.txt', 'a')
                        f.write(report + "\n")
                        f.close()
                        break

                if message.text.upper() != user_login and message.text != switches['pass'][ind]:
                    await message.answer("Пароль не верен! ¯\_(ツ)_/¯")
            except :
                await message.answer("Регистрация не возможна в данный момент😕")
                print('Файл с пользователями не обнаружен!')






async def scheduler():
    aioschedule.every().day.at("20:00").do(evening_reminder)  # время срабатывания вечернего напоминания
    aioschedule.every().day.at("05:30").do(morning_reminder)  # время срабатывания вечернего напоминания
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


async def evening_reminder():
    try:
        switches = pd.read_csv('VKS.csv', delimiter=';')
        tomorrowdate = datetime.date.today() + datetime.timedelta(days=1)  # получаем текущую дату
        for ind in switches.index:
            if switches['date'][ind] == str(tomorrowdate.strftime("%d.%m.%Y")):  # ищем в файле сторку с завтрашней датой
                users = pd.read_csv('Users.csv', delimiter=';')
                for ind1 in users.index:
                    if users['login'][ind1] == switches['name'][ind]:

                        if str(users['tg_id'][ind1]) !='nan' and users['notification'][ind1] == 1:
                            answer = "Добрый вечер " + switches['name'][ind] + "! Напоминание на завтра:\n Задача - ВКС, Прибытие - 7:00 " + str(tomorrowdate.strftime("%d.%m.%Y"))
                            await bot.send_message(chat_id=int(users['tg_id'][ind1]), text=answer)
                            report = "Вечернее напоминание " + switches['name'][ind] + " отправлено в " + str(tomorrowdate.strftime("%d.%m.%Y"))
                            print(report)
                            f = open('report.txt', 'a')
                            f.write(report + "\n")
                            f.close()



    except FileNotFoundError:
        print('Файл с расписанием не обнаружен!')


async def morning_reminder():
    try:
        switches = pd.read_csv('VKS.csv', delimiter=';')
        today = now.strftime("%d.%m.%Y")  # получаем текущую дату
        for ind in switches.index:
            if switches['date'][ind] == str(
                    today):  # ищем в файле сторку с завтрашней датой
                users = pd.read_csv('Users.csv', delimiter=';')
                for ind1 in users.index:
                    if users['login'][ind1] == switches['name'][ind]:

                        if str(users['tg_id'][ind1]) != 'nan' and users['notification'][ind1] == 1:
                            answer = "Доброе утро " + switches['name'][
                                ind] + "! Напоминание:\n Задача - ВКС, Прибытие - 7:00 " + str(today)
                            await bot.send_message(chat_id=int(users['tg_id'][ind1]), text=answer)
                            report = "Утреннее напоминание " + switches['name'][ind] + " отправлено в " + str(today)
                            print(report)
                            f = open('report.txt', 'a')
                            f.write(report + "\n")
                            f.close()



    except FileNotFoundError:
        print('Файл с расписанием не обнаружен!')



if __name__ == '__main__':
    print('Бот запущен!')
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
