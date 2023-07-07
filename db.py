import sqlite3

class BotDB:
	def __init__(self, db_file):
		"""Инициализация соединения с БД"""
		self.conn = sqlite3.connect(db_file)
		self.cursor = self.conn.cursor()




	def user_exists(self, user_id):
		"""Проверка на наличие пользователя"""
		result = self.cursor.execute("SELECT 'idd' FROM 'user' WHERE user_id = ?", (user_id,))
		return bool(len(result.fetchall()))




	def get_user_id(self, user_id):
		"""Получаем id юзера в базе по id в телеграмме"""
		with sqlite3.connect('accountant.db') as cursor:
			result = cursor.execute("SELECT idd FROM 'user' WHERE user_id = ?", (user_id,))
			result = result.fetchone() 
			result = int(result[0])
			return result


	def get_password(self, idd):
		"""Получаем password юзера в базе по id """
		with sqlite3.connect('accountant.db') as cursor:
			result = cursor.execute("SELECT password FROM 'user' WHERE idd = ?", (idd,))
			return result.fetchall()[0]




	def add_user(self, user_id):
		"""Добовляем юзера в БД"""
		self.cursor.execute("INSERT INTO 'user' ('user_id') VALUES(?)", (user_id,))
		return self.conn.commit()


	def db_inserter(self, user_id, username, first_name, last_name, password):

		if username is None:
			username = 'None'
			print(type(username))
		if first_name is None:
			first_name = 'None'
			print(type(first_name))
		if last_name is None:
			last_name = 'None'
			print(type(last_name))

		with sqlite3.connect('accountant.db') as conn:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO 'user' ('user_id', 'username', 'name', 'password') VALUES (?, ?, ?, ?)", (user_id, username, first_name + last_name, password))
			# Фиксация изменений в базе данных
			conn.commit()

	def db_eventer(self, user_id, time_now, eve_date, eve_name, eve_disc):

		with sqlite3.connect('accountant.db') as conn:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO 'event' ('user_id', 'event_date', 'set_date', 'event_description', 'event_name') VALUES (?, ?, ?, ?, ?)", (user_id, eve_date, time_now, eve_disc, eve_name))
			# Фиксация изменений в базе данных
			conn.commit()


	def db_list(self, user_id):

		with sqlite3.connect('accountant.db') as conn:
			cursor = conn.cursor()
			result = cursor.execute("SELECT * FROM 'event' WHERE user_id = ?", (user_id,))
			result = result.fetchall()
			return result


	def db_delete_row(self, idd):
		idd = int(idd[0])
		with sqlite3.connect('accountant.db') as conn:
			with sqlite3.connect('accountant.db') as cursor:
				query = f"DELETE FROM 'event' WHERE id = ?"
				cursor.execute(query, (idd,))
				conn.commit()


	def db_list_id(self, idd):
		with sqlite3.connect('accountant.db') as conn:
			cursor = conn.cursor()
			result = cursor.execute("SELECT * FROM 'event' WHERE id = ?", (idd,))
			result = result.fetchall()
			return result


	def db_tasker(self, user_id, task_disc, task_pri, date_now):
		with sqlite3.connect('accountant.db') as conn:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO 'task' ('user_id', 'task_description', 'priority','set_date') VALUES (?, ?, ?, ?)", (user_id, task_disc, task_pri, date_now))
			# Фиксация изменений в базе данных
			conn.commit()
		

	def db_task_list(self, user_id):
		with sqlite3.connect('accountant.db') as conn:
			cursor = conn.cursor()
			result = cursor.execute("SELECT * FROM 'task' WHERE user_id = ?", (user_id,))
			result = result.fetchall()
			return result


	def db_compliting(self, task, date):
		user_id = task[1]
		idd = task[0]
		dis = task[2]
		with sqlite3.connect('accountant.db') as conn:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO 'task_done' ('user_id', 'complit_date', 'task_id', 'task_description') VALUES (?, ?, ?, ?)", (user_id, date, idd, dis))
			query = f"DELETE FROM 'task' WHERE id = ?"
			cursor.execute(query, (idd,))
			conn.commit()


	def db_task_done_list(self, user_id):

		with sqlite3.connect('accountant.db') as conn:
			cursor = conn.cursor()
			result = cursor.execute("SELECT * FROM 'task_done' WHERE user_id = ?", (user_id,))
			result = result.fetchall()
			return result


	def db_rep_ev_seter(self, user_id, name, eve_date):
		with sqlite3.connect('accountant.db') as conn:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO 'repit_event' ('user_id', 'name', 'date_repit') VALUES (?, ?, ?)", (user_id, name, eve_date))
			# Фиксация изменений в базе данных
			conn.commit()