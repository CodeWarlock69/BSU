import telebot
from telebot import types
import sqlite3
from db import BotDB
import hashlib
import datetime


# from password import hash_password
# from password import verify_password
#import bot_script 


#cd D:\1Practica
#d:


# + ТГ - Бот позволяет пользователю зарегистрироваться и хранит его логин и пароль.
# + Безопасное хранение паролей в БД (шифрование, хэш).
# + Хранение календаря пользователя на месяц. Создание, редактирование, и визуализация событий для каждого пользователя.
# + Возможность задать повторяющиеся события.
# + Хранение задач не привязанных ко времени с приоритетом.
# + Подведение итогов недели для пользователя.
# + Поиск свободных окон в графике пользователя.
# + Приложение запускается на локальном сервере.


bot_db = BotDB('accountant.db')
bot = telebot.TeleBot('5991552613:AAGp0X2onDO8D_ujRa8f0OTAwTDtwHo9sA4')
states = {}
tg_date = datetime.datetime(1970, 1, 1)






#_________________________________________________Хэш функции
def hash_password(password):
    """Хеширует пароль и возвращает его хэш"""
   
    password_bytes = password.encode('utf-8')        # Преобразование пароля в байтовую строку 
    hash_object = hashlib.sha256()                   # Создание объекта хэша
    hash_object.update(password_bytes)               # Обновление хэша с байтами пароля
    password_hash = hash_object.hexdigest()          # Получение хэша в виде шестнадцатеричной строки

    return password_hash



def verify_password(password, password_hash):
    """Проверяет, соответствует ли пароль его хэшу"""
    
    hashed_password = hash_password(password)        # Хеширование введенного пароля
    if hashed_password == password_hash:             # Сравнение хэшей
        return True
    else:
        return False
#_________________________________________________






#_________________________________________________Функции для работы с датами
def split_date_time(date_time_string):
    date_parts = date_time_string.split()[0].split('-')
    year = int(date_parts[0])
    month = int(date_parts[1])
    day = int(date_parts[2])
    return year, month, day




def get_distance_to_boundaries(number):
    # Проверка, что число находится в диапазоне от 0 до 6
    if number < 0 or number > 6:
        raise ValueError('Число должно быть от 0 до 6')
    left_distance = number
    right_distance = 6 - number
    return left_distance, right_distance
#_________________________________________________

 




#_________________________________________________Старт
@bot.message_handler(commands=['start'])
def start(message):
	mess = f'Привет, <b>{message.from_user.first_name}</b>. Вас приветствует бот-календарь, который поможет вам следить за вашим распорядком дня. Чтобы начать использовать бота, пройдите регистрацию. Сделать это можно с помошью кнопки "<b>/signin</b>", которая находится в меню или написав "<b>/signin</b>" в чат. Если вы уже регистрировались, выберите "/login"'
	bot.send_message(message.chat.id, mess, parse_mode='html')
#_________________________________________________Хэш функции






#____________________________________________________Регистрация
@bot.message_handler(commands=['signin'])
def signin(message):
    states[message.chat.id] = 'remember'
    mess = f'Придумайте пароль'
    bot.send_message(message.chat.id, mess, parse_mode='html')



@bot.message_handler(func=lambda message: states.get(message.chat.id) == 'remember')
def save_text(message):
    passw = message.text
    password = hash_password(passw)
    # Получаем данные пользователя
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Выводим данные пользователя
    response = f'Регистрация завершена!\n\n' \
               f'ID: {user_id}\n' \
               f'Username: @{username}\n' \
               f'Имя: {first_name}\n' \
               f'Фамилия: {last_name}\n' \
               f'Пароль: {passw}'
    
    # Отправляем ответ пользователю
    bot.send_message(message.chat.id, response)
    bot_db.db_inserter(user_id, username, first_name, last_name, password)
    states[message.chat.id] = None
#________________________________________________________






#____________________________________________________Вход
@bot.message_handler(commands=['login'])
def login(message):
    states[message.chat.id] = '2'
    mess = f'Введите пароль'
    bot.send_message(message.chat.id, mess, parse_mode='html')



@bot.message_handler(func=lambda message: states.get(message.chat.id) == '2')
def save_text(message):
    passw = message.text

    idUser = bot_db.get_user_id(message.from_user.id)
    password = bot_db.get_password(idUser)
    password = str(password[0])

    if verify_password(passw, password):
    	bot.send_message(message.chat.id, 'Верный пароль', parse_mode='html')
    else: 
    	bot.send_message(message.chat.id, 'Не верный пароль', parse_mode='html')

    
    states[message.chat.id] = None
#_________________________________________________






#____________________________________________________Проверка на вход

#____________________________________________________






#____________________________________________________Проверка на актуальность мероприятия 

#____________________________________________________






#_________________________________________________________________________________________Задать мероприятие 
@bot.message_handler(commands=['event'])
def event(message):
    states[message.chat.id] = '3'
    mess = f'Введите дату и время вашего мероприятия (ДД/ММ/ГГГГ ЧЧ:ММ:СС)'
    bot.send_message(message.chat.id, mess, parse_mode='html')



@bot.message_handler(func=lambda message: states.get(message.chat.id) == '3')
def save_text(message):
    global user_id, time_now, eve_date
    eve_date = message.text
    user_id = message.from_user.id
    time_now = message.date
    time_now = tg_date + datetime.timedelta(seconds=time_now, hours=3)
    eve_date = datetime.datetime.strptime(eve_date, "%d/%m/%Y %H:%M:%S")
    states[message.chat.id] = '4'
    mess = f'Введите название мероприятия'
    bot.send_message(message.chat.id, mess, parse_mode='html')
    bot.register_next_step_handler(message, event_name)



@bot.message_handler(func=lambda message: states.get(message.chat.id) == '4')
def event_name(message):
    global eve_name
    eve_name = message.text
    states[message.chat.id] = '5'
    mess = f'Введите краткое описание мероприятия'
    bot.send_message(message.chat.id, mess, parse_mode='html')
    bot.register_next_step_handler(message, event_dis)



@bot.message_handler(func=lambda message: states.get(message.chat.id) == '5')
def event_dis(message):
    global user_id, time_now, eve_date, eve_name
    eve_disc = message.text
    response = f'Отлично!\n\n' \
               f'Текущая дата: {time_now}\n' \
               f'Дата мероприятия: {eve_date}\n' \
               f'Название мероприятия: {eve_name}\n' \
               f'Описание мероприятия: {eve_disc}\n'
    bot.send_message(message.chat.id, response)
    bot_db.db_eventer(user_id, time_now, eve_date, eve_name, eve_disc)


    states[message.chat.id] = None
#_________________________________________________________________________________________






#_________________________________________________________________________________________Список мероприятий
@bot.message_handler(commands=['list'])
def list(message):
	user_id = message.from_user.id
	lists = bot_db.db_list(user_id)\

	if len(lists) == 0:
		bot.send_message(message.chat.id, 'У вас нет мероприятий', parse_mode='html')
	else:
		i = len(lists)
		k = len(lists[0])
		for item in lists:
			response = f'1.Дата мероприятия: {item[2]}\n' \
	                   f'2.Текущая дата: {item[3]}\n' \
	                   f'3.Название мероприятия: {item[5]}\n' \
	                   f'4.Описание мероприятия: {item[4]}\n'
			bot.send_message(message.chat.id, response, parse_mode='html')
#_________________________________________________________________________________________






#_________________________________________________________________________________________Редактирование мероприятия
@bot.message_handler(commands=['edit'])
def edit(message):
    user_id = message.from_user.id
    global lists
    lists = bot_db.db_list(user_id)
    i = len(lists)
    k = len(lists[0])
    for item in lists:
        response = f'Номер: {item}\n' \
        		   f'1. Дата мероприятия: {item[2]}\n' \
                   f'2. Текущая дата: {item[3]}\n' \
                   f'3. Название мероприятия: {item[5]}\n' \
                   f'4. Описание мероприятия: {item[4]}\n'
        bot.send_message(message.chat.id, response, parse_mode='html')

    states[message.chat.id] = '6'
    mess = f'Выберете номер мероприятия для редактирования'
    bot.send_message(message.chat.id, mess, parse_mode='html')



@bot.message_handler(func=lambda message: states.get(message.chat.id) == '6')
def editing(message):
    numb = int(message.text)
    response = f'1. Дата мероприятия: {lists[numb-1][2]}\n' \
               f'2. Текущая дата: {lists[numb-1][3]}\n' \
               f'3. Название мероприятия: {lists[numb-1][5]}\n' \
               f'4. Описание мероприятия: {lists[numb-1][4]}\n'
    bot.send_message(message.chat.id, response, parse_mode='html')
    bot_db.db_delete_row(lists[numb-1])
    states[message.chat.id] = None


    
    event(message)
#_________________________________________________________________________________________






#_________________________________________________________________________________________Удаление
@bot.message_handler(commands=['delet'])
def delet(message):
    user_id = message.from_user.id
    global lists
    lists = bot_db.db_list(user_id)
    i = len(lists)
    k = len(lists[0])
    j = 1
    for item in lists:
        response = f'Номер: {j}\n' \
        		   f'1. Дата мероприятия: {item[2]}\n' \
                   f'2. Текущая дата: {item[3]}\n' \
                   f'3. Название мероприятия: {item[5]}\n' \
                   f'4. Описание мероприятия: {item[4]}\n'
        bot.send_message(message.chat.id, response, parse_mode='html')
        j += 1

    states[message.chat.id] = '7'
    mess = f'Выберете номер мероприятия для удаления'
    bot.send_message(message.chat.id, mess, parse_mode='html')



@bot.message_handler(func=lambda message: states.get(message.chat.id) == '7')
def editing(message):
    numb = int(message.text)
    response = f'1. Дата мероприятия: {lists[numb-1][2]}\n' \
               f'2. Текущая дата: {lists[numb-1][3]}\n' \
               f'3. Название мероприятия: {lists[numb-1][5]}\n' \
               f'4. Описание мероприятия: {lists[numb-1][4]}\n'
    bot.send_message(message.chat.id, response, parse_mode='html')
    bot_db.db_delete_row(lists[numb-1])
    states[message.chat.id] = None
#_________________________________________________________________________________________






#_________________________________________________________________________________________Расписание на неделю
@bot.message_handler(commands=['week_list'])
def week_list(message):
    date_now = message.date
    date_now = tg_date + datetime.timedelta(seconds=date_now, hours=3)
    date_now = str(date_now)
    date_now, time_str = date_now.split(' ')
    user_id = message.from_user.id
    ev_list = bot_db.db_list(user_id)
    id_list = []
    monday, tuesday, wednesday, thursday, friday, saturday, sunday = [], [], [], [], [], [], []

    date = datetime.datetime.strptime(date_now, '%Y-%m-%d').date()
    weekday_number = date.weekday() # Получение номера дня недели (0 - понедельник, 1 - вторник, ..., 6 - воскресенье)

    for item in ev_list:
        year_now, month_now, day_now = split_date_time(date_now)
        year_eve, month_eve, day_eve = split_date_time(item[2])
        if year_eve == year_now:
            if month_eve == month_now:
                date = datetime.datetime.strptime(date_now, '%Y-%m-%d').date()
                weekday_number = date.weekday()
                left_distance, right_distance = get_distance_to_boundaries(weekday_number)
                if day_eve >= day_now - left_distance and day_eve <= day_now + right_distance:
                    id_list.append(item[0]) 

    for ev in id_list:
        evenk = bot_db.db_list_id(ev)
        date = evenk[0][2]
        date, t = date.split(' ')
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        weekday_number = date.weekday()
        if weekday_number == 0:
            monday.append(evenk)
        elif weekday_number == 1:
            tuesday.append(evenk)
        elif weekday_number == 2:
            wednesday.append(evenk)
        elif weekday_number == 3:
            thursday.append(evenk)
        elif weekday_number == 4:
            friday.append(evenk)
        elif weekday_number == 5:
            saturday.append(evenk)
        elif weekday_number == 6:
            sunday.append(evenk)

    response = ''
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    week = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]
    for i, day in enumerate(week):
        response += f'\n{days[i]}:\n'
        if day:
            for event in day:
                response += '\t- Мероприятия:\n'
                response += f'\t           1. Дата мероприятия: {event[0][2]}\n'
                response += f'\t           2. Текущая дата: {event[0][3]}\n'
                response += f'\t           3. Название мероприятия: {event[0][5]}\n'
                response += f'\t           4. Описание мероприятия: {event[0][4]}\n'
        else:
            response += '\t-\n'

    bot.send_message(message.chat.id, response, parse_mode='html')
#_________________________________________________________________________________________






#_________________________________________________________________________________________Свободное время на неделе
@bot.message_handler(commands=['free_list'])
def free_list(message):
    date_now = message.date
    date_now = tg_date + datetime.timedelta(seconds=date_now, hours=3)
    date_now = str(date_now)
    date_now, time_str = date_now.split(' ')
    user_id = message.from_user.id
    ev_list = bot_db.db_list(user_id)
    id_list = []
    monday, tuesday, wednesday, thursday, friday, saturday, sunday = [], [], [], [], [], [], []

    date = datetime.datetime.strptime(date_now, '%Y-%m-%d').date()
    weekday_number = date.weekday() # Получение номера дня недели (0 - понедельник, 1 - вторник, ..., 6 - воскресенье)

    for item in ev_list:
        year_now, month_now, day_now = split_date_time(date_now)
        year_eve, month_eve, day_eve = split_date_time(item[2])
        if year_eve == year_now:
            if month_eve == month_now:
                date = datetime.datetime.strptime(date_now, '%Y-%m-%d').date()
                weekday_number = date.weekday()
                left_distance, right_distance = get_distance_to_boundaries(weekday_number)
                if day_eve >= day_now - left_distance and day_eve <= day_now + right_distance:
                    id_list.append(item[0]) 

    for ev in id_list:
        evenk = bot_db.db_list_id(ev)
        date = evenk[0][2]
        date, t = date.split(' ')
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        weekday_number = date.weekday()
        if weekday_number == 0:
            monday.append(evenk)
        elif weekday_number == 1:
            tuesday.append(evenk)
        elif weekday_number == 2:
            wednesday.append(evenk)
        elif weekday_number == 3:
            thursday.append(evenk)
        elif weekday_number == 4:
            friday.append(evenk)
        elif weekday_number == 5:
            saturday.append(evenk)
        elif weekday_number == 6:
            sunday.append(evenk)

    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    week = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]
    response = ''
    for i, day in enumerate(week):
	    response += f'\n{days[i]}:\n'
	    if day:
	        response += f'\t         Количество мероприятий:     {len(day)}\n'
	    else:
	        response += '\t         Количество мероприятий:     0\n'
    bot.send_message(message.chat.id, response, parse_mode='html')
#_________________________________________________________________________________________






#_________________________________________________________________________________________Создать задачу
@bot.message_handler(commands=['task'])
def task(message):
	states[message.chat.id] = '9'
	mess = f'Введите описание задачи'
	bot.send_message(message.chat.id, mess, parse_mode='html')


@bot.message_handler(func=lambda message: states.get(message.chat.id) == '9')
def task_disc(message):
	global task_dis
	task_dis = message.text
	states[message.chat.id] = '10'
	mess = f'Введите приоретет задачи (от 0 да 10)'
	bot.send_message(message.chat.id, mess, parse_mode='html')


@bot.message_handler(func=lambda message: states.get(message.chat.id) == '10')
def task_pri(message):
	date_now = message.date
	date_now = tg_date + datetime.timedelta(seconds=date_now, hours=3)
	date_now = str(date_now)
	task_pri = int(message.text)
	user_id = message.from_user.id
	states[message.chat.id] = None
	bot_db.db_tasker(user_id,task_dis,task_pri, date_now)
	mess = f'Задача добавлена'
	bot.send_message(message.chat.id, mess, parse_mode='html')
#_________________________________________________________________________________________






#_________________________________________________________________________________________Просмотреть список задач
@bot.message_handler(commands=['task_list'])
def task(message):
	user_id = message.from_user.id
	t_list = bot_db.db_task_list(user_id)
	response = ''
	priority_levels = set(task[3] for task in t_list)  # Получаем уникальные уровни важности задач

	for priority in sorted(priority_levels, reverse=True):
	    response += f'\nУровень приоретета {priority}: \n'
	    tasks = [task[2] for task in t_list if task[3] == priority]
	    if tasks:
	        for task in tasks:
	            response += f'\t   -{task}\n'
	    else:
	        response += '\tПеречень задач пуст\n'
	bot.send_message(message.chat.id, response, parse_mode='html')
#_________________________________________________________________________________________






#_________________________________________________________________________________________Выполнить задачу
@bot.message_handler(commands=['task_complit'])
def task_complit(message):
	user_id = message.from_user.id
	t_list = bot_db.db_task_list(user_id)
	k = 1
	response = ''
	priority_levels = set(task[3] for task in t_list)  # Получаем уникальные уровни важности задач

	for priority in sorted(priority_levels, reverse=True):
	    response += f'\nУровень приоретета {priority}: \n'
	    tasks = [task[2] for task in t_list if task[3] == priority]
	    if tasks:
	        for task in tasks:
	            response += f'\t   -№{k} {task}\n'
	            k += 1
	    else:
	        response += '\tПеречень задач пуст\n'
	bot.send_message(message.chat.id, "Выберите номер задачи, которую хотите выполнить", parse_mode='html')
	bot.send_message(message.chat.id, response, parse_mode='html')
	states[message.chat.id] = '11'



@bot.message_handler(func=lambda message: states.get(message.chat.id) == '11')
def task_с(message):
	k = int(message.text)
	time_now = message.date
	time_now = tg_date + datetime.timedelta(seconds=time_now, hours=3)
	user_id = message.from_user.id
	t_list = bot_db.db_task_list(user_id)
	states[message.chat.id] = None
	j = 0
	response = ''
	priority_levels = set(task[3] for task in t_list)  # Получаем уникальные уровни важности задач

	for priority in sorted(priority_levels, reverse=True):
	    response += f'\nУровень приоретета {priority}: \n'
	    tasks = [task for task in t_list if task[3] == priority]
	    if tasks:
	        for task in tasks:
	            response += f'\t   -{task}\n'
	            j += 1
	            if j == k:
	            	bot_db.db_compliting(task, time_now)
	    else:
	        response += '\tПеречень задач пуст\n'

	bot.send_message(message.chat.id, "Задача выполнена", parse_mode='html')            
#_________________________________________________________________________________________






#_________________________________________________________________________________________Итоги недели(мероприятия + задачи)
@bot.message_handler(commands=['week_results'])
def week_results(message):
	date_now = message.date
	date_now = tg_date + datetime.timedelta(seconds=date_now, hours=3)
	date_now = str(date_now)
	date_now, time_str = date_now.split(' ')
	user_id = message.from_user.id
	ev_list = bot_db.db_list(user_id)
	id_list = []
	t_list = bot_db.db_task_list(user_id)
	td_list = bot_db.db_task_done_list(user_id)



	#______________Мероприятий посещенно______________#
	date = datetime.datetime.strptime(date_now, '%Y-%m-%d').date()
	weekday_number = date.weekday() # Получение номера дня недели (0 - понедельник, 1 - вторник, ..., 6 - воскресенье)

	for item in ev_list:
	    year_now, month_now, day_now = split_date_time(date_now)
	    year_eve, month_eve, day_eve = split_date_time(item[2])
	    if year_eve == year_now:
	        if month_eve == month_now:
	            date = datetime.datetime.strptime(date_now, '%Y-%m-%d').date()
	            weekday_number = date.weekday()
	            left_distance, right_distance = get_distance_to_boundaries(weekday_number)
	            if day_eve >= day_now - left_distance and day_eve <= day_now + right_distance:
	                id_list.append(item[0])
	event_was = len(id_list)
	id_list = []
	#_________________________________________________#



	#______________Мероприятий заплонированно______________#
	for item in ev_list:
	    year_now, month_now, day_now = split_date_time(date_now)
	    year_eve, month_eve, day_eve = split_date_time(item[3])
	    if year_eve == year_now:
	        if month_eve == month_now:
	            date = datetime.datetime.strptime(date_now, '%Y-%m-%d').date()
	            weekday_number = date.weekday()
	            left_distance, right_distance = get_distance_to_boundaries(weekday_number)
	            if day_eve >= day_now - left_distance and day_eve <= day_now + right_distance:
	                id_list.append(item[0])
	event_will = len(id_list)
	id_list = []
	#______________________________________________________#



	#______________Задач поставленно______________#
	for item in t_list:
	    year_now, month_now, day_now = split_date_time(date_now)
	    year_eve, month_eve, day_eve = split_date_time(item[4])
	    if year_eve == year_now:
	        if month_eve == month_now:
	            date = datetime.datetime.strptime(date_now, '%Y-%m-%d').date()
	            weekday_number = date.weekday()
	            left_distance, right_distance = get_distance_to_boundaries(weekday_number)
	            if day_eve >= day_now - left_distance and day_eve <= day_now + right_distance:
	                id_list.append(item[0])
	task_will = len(id_list)
	id_list = []
	#_____________________________________________#



	#______________Задач выполнено______________#
	for item in td_list:
	    year_now, month_now, day_now = split_date_time(date_now)
	    year_eve, month_eve, day_eve = split_date_time(item[2])
	    if year_eve == year_now:
	        if month_eve == month_now:
	            date = datetime.datetime.strptime(date_now, '%Y-%m-%d').date()
	            weekday_number = date.weekday()
	            left_distance, right_distance = get_distance_to_boundaries(weekday_number)
	            if day_eve >= day_now - left_distance and day_eve <= day_now + right_distance:
	                id_list.append(item[0])
	task_was = len(id_list)
	id_list = []
	#___________________________________________#



	response = f'Результаты этой недели \n\n' \
			   f'Мероприятий посещенно:    {event_was}\n' \
	           f'Мероприятий заплонированно:    {event_will}\n' \
	           f'Задач поставленно:    {task_will}\n' \
	           f'Задач выполнено:    {task_was}\n\n' \
	           f'Продолжайте в том же духе\n'
	bot.send_message(message.chat.id, response, parse_mode='html')
#_________________________________________________________________________________________






#_________________________________________________________________________________________Повторяющееся событие 
@bot.message_handler(commands=['repit_event'])
def repit_event(message):
	states[message.chat.id] = '15'
	mess = f'Введите название события, которое будет повторяться'
	bot.send_message(message.chat.id, mess, parse_mode='html')



@bot.message_handler(func=lambda message: states.get(message.chat.id) == '15')
def rep_ev(message):
	global name
	name = message.text
	states[message.chat.id] = '16'
	mess = f'Введите дату для уведомления (ДД/ММ/ГГГГ ЧЧ:ММ:СС)'
	bot.send_message(message.chat.id, mess, parse_mode='html')



@bot.message_handler(func=lambda message: states.get(message.chat.id) == '16')
def rep_ev_set(message):
	user_id = message.from_user.id
	eve_date = message.text
	eve_date = datetime.datetime.strptime(eve_date, "%d/%m/%Y %H:%M:%S")
	bot_db.db_rep_ev_seter(user_id, name, eve_date)

	bot.send_message(message.chat.id, 'Мероприятие создано', parse_mode='html')
#_________________________________________________________________________________________
bot.polling(non_stop=True)
