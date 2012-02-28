#!/usr/bin/env python

import tornado.httpserver
import tornado.web
import tornado.database


class ExampleHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def get(self):
		uid = self.get_argument("id", None)
		turkId = self.get_argument("tid", None)

		if (not uid) or (not turkId): return None;

		# check the turkID
		user = self.db.get( "SELECT * FROM personality WHERE turkID = %s", turkId )

		if not user:
			self.write("Invalid request 404")
			return None
		else:
			if int(user["uid"]) == int(uid):
				self.render("example.html", turkID=turkId)
				return None
			return None