#!/usr/bin/env python

import tornado.httpserver
import tornado.web
import tornado.database

class WatchHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def get(self):
		self.render("watch.html")

	def post(self):
		turkId = self.get_argument("tid", None)
		vid = self.get_argument("vid", None)
		bc = self.get_argument("bc", None)

		if (not turkId) or (not vid) or (not bc):
			return None

		try:
			self.db.execute(
				"INSERT INTO feedback (turkID, video, feedback) VALUES (%s, %s, %s)", turkId, vid, bc
			)
		except Exception, exception:
			print exception
			return None
