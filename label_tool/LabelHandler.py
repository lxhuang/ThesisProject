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
		self.render("label.html")

	def post(self):
		pass