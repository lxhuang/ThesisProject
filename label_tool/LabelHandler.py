#!/usr/bin/env python

import tornado.httpserver
import tornado.web
import tornado.database

class LabelHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def get(self):
		root_path = "https://s3.amazonaws.com/multicomp_backchannel_videos/"
		file_name = self.get_argument("v", None)
		anno_type = self.get_argument("t", None)
		if (not file_name) or (not anno_type):
			return
		file_path = root_path + file_name + ".mp4"
		self.render("annotation.html", file_path=file_path, file_name=file_name, type=anno_type)

	def post(self):
		video_name = self.get_argument("v", None)
		anno_type = self.get_argument("t", None)
		label_str = self.get_argument("l", "")
		if (not anno_type) or (not label_str):
			return

		try:
			label_id = self.db.execute(
				"INSERT INTO label (video_name, type, content) VALUES (%s, %s, %s)", video_name, anno_type, label_str
			)
			self.write("{\"label_id\" : \""+str(label_id)+"\"}")
		except Exception, exception:
			print exception
			return None