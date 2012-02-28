#!/usr/bin/env python

import tornado.httpserver
import tornado.web
import tornado.database


class PSIHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def post(self):
		turkId = self.get_argument("tid", None)
		vid = self.get_argument("vid", None)
		psi = self.get_argument("psi", None)

		if (not turkId) or (not vid) or (not psi):
			return None

		try:
			self.db.execute(
				"INSERT INTO psi (turkID, vid, psi) VALUES (%s, %s, %s)", turkId, vid, psi
			)
			self.write("{\"success\":\"1\"}")
		except Exception, exception:
			print exception
			self.write("{\"err\":\"error in inserting into psi table\"}")
		
		return None