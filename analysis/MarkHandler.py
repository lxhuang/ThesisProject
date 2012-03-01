#!/usr/bin/env python
import tornado.httpserver
import tornado.web
import tornado.database
import json

class MarkHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def post(self):
		mid     = self.get_argument("mid", None)
		vid     = self.get_argument("vid", None)
		time    = self.get_argument("time", None)
		turkId  = self.get_argument("turkID", None)
		comment = self.get_argument("comment", None)
		
		if not mid:
			if not vid or not comment: return
			if not turkId:
				turkId = ""
			if not time:
				time = 0.0

			try:
				mid = self.db.execute(
					"INSERT INTO mark (vid, turkID, time, comment) VALUES (%s, %s, %s, %s)", vid, turkId, float(time), comment
				)
				ret = {"id": mid}
				self.write( json.dumps( ret ) )

			except Exception, exception:
				print exception
		else:
			try:
				if mid == "-1":
					marks = self.db.query("SELECT * FROM mark")
					self.write( json.dumps(marks) )
				else:
					self.db.get("DELETE FROM mark WHERE mid = %s", int(mid))
			except Exception, exception:
				print exception