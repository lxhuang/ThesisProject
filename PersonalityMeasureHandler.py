#!/usr/bin/env python

import tornado.httpserver
import tornado.web
import tornado.database

class PersonalityMeasureHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def get(self):
		self.render("pq.html")

	def post(self):
		turkId = self.get_argument("turkId", None)
		age = self.get_argument("age", None)
		sex = self.get_argument("sex", None)
		personality = self.get_argument("result", None)
		
		if (not turkId) or (not age) or (not sex) or (not personality):
			self.write("{\"err\":\"invalid arguments\"}")
			return None

		age = int(age)

		try:
			uid = self.db.execute(
				"INSERT INTO personality (turkID, age, sex, personality) VALUES (%s, %s, %s, %s)", turkId, age, sex, personality
			)

			self.write("{\"res\":" + str(uid) + "}")
			return None
		except Exception, exception:
			print exception.args
			print exception
			self.write("{\"err\":\"you have participated in this experiment\"}")
			return None
