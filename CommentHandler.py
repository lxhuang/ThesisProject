#!/usr/bin/env python

import tornado.httpserver
import tornado.web
import tornado.database

import random

code = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

class CommentHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def randomCode(self):
		c = []
		random.seed()
		for i in range(1,27):
			index = random.randint(1, 26)
			c.append( code[index-1] )

		return "".join(c)

	def get(self):
		self.render("comment.html")

	def post(self):
		turkId = self.get_argument("tid", None)
		comment = self.get_argument("comment", None)

		if not turkId: return None

		try:
			feedback = self.db.query(
				"SELECT * FROM feedback WHERE turkID = %s", turkId
			)
			if len(feedback) < 8:
				self.write( "{\"err\" : \"you have not finished all videos yet\"}" )
				return None

			self.db.execute(
				"INSERT INTO comment (turkID, comment) VALUES (%s, %s)", turkId, comment
			)

			# generate the verification code
			c = self.randomCode()
			# save the code into database
			self.db.execute(
				"INSERT INTO verify (turkID, code) VALUES (%s, %s)", turkId, c
			)

			self.write( "{\"code\":\"" + c + "\"}" )

		except Exception, exception:
			print exception
			return None
