#!/usr/bin/env python

import os
import tornado.database
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options

from MainHandler import MainHandler
from UpdateHandler import UpdateHandler
from UpdateHandler import NewMessageHandler
from MarkHandler import MarkHandler

define("port", default=8483, type=int)
define("mysql_host", default="23.21.246.188:3306")
define("mysql_database", default="mturk")
define("mysql_user", default="root")
define("mysql_password", default="")

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/new", NewMessageHandler),
			(r"/update", UpdateHandler),
			(r"/mark", MarkHandler),
		]

		settings = dict(
			title = "University of Southern California, Human Behavior Study",
			base_url = "http://localhost:8483/",
			static_path = os.path.join(os.path.dirname(__file__), "static"),
			template_path = os.path.join(os.path.dirname(__file__), "templates"),
		)

		tornado.web.Application.__init__(self, handlers, **settings)

		self.db = tornado.database.Connection(
			host = options.mysql_host,
			database = options.mysql_database,
			user = options.mysql_user,
			password = options.mysql_password
		)
	
def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()	
