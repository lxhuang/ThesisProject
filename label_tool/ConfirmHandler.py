#!/usr/bin/env python

import tornado.httpserver
import tornado.web
import tornado.database

import random

code = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9']

class ConfirmHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def randomCode(self):
		c = []
		random.seed()
		for i in range(1,37):
			index = random.randint(1, 36)
			c.append( code[index-1] )

		return "".join(c)

	def get(self):
		label_id = self.get_argument('label_id', None)
		video_name = self.get_argument('v', None)
		if (not label_id) or (not video_name):
			return

		code = self.randomCode()

		try:
			self.db.execute(
				"INSERT INTO verify (label_id, code) VALUES (%s, %s)", label_id, code
			)
			self.render("confirm.html", code=code, video_name=video_name)
		except Exception, exception:
			print exception
			return