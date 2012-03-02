#!/usr/bin/env python

import os
import tornado.database
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

from WelcomeHandler import WelcomeHandler
from PersonalityMeasureHandler import PersonalityMeasureHandler
from ExampleHandler import ExampleHandler
from TaskHandler import TaskHandler
from WatchHandler import WatchHandler
from CommentHandler import CommentHandler
from PSIHandler import PSIHandler

define("port", default=80, type=int)
define("mysql_host", default="127.0.0.1:3306")
define("mysql_database", default="mturk")
define("mysql_user", default="root")
define("mysql_password", default="")

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", WelcomeHandler),
			(r"/pq", PersonalityMeasureHandler),
			(r"/example", ExampleHandler),
			(r"/task", TaskHandler),
			(r"/watch", WatchHandler),
			(r"/comment", CommentHandler),
			(r"/psi", PSIHandler),
		]

		settings = dict(
			title = "University of Southern California, Human Behavior Study",
			base_url = "http://23.21.246.188:80/",
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
