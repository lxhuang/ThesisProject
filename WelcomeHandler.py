
#!/usr/bin/env python

import tornado.httpserver
import tornado.web

class WelcomeHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("welcome.html")