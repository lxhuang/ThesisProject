#!/usr/bin/env python
import tornado.httpserver
import tornado.web
import tornado.database
import json
import uuid

class MessageMixin(object):
	waiters = set()
	cache = []
	cache_size = 1024

	def wait_for_messages(self, callback, cursor=None):
		cls = MessageMixin
		
		if cursor:
			found = 0
			index = 0
			for i in range(0,len(cls.cache)):
				index = len(cls.cache) - 1 - i
				if cls.cache[index]["id"] == cursor:
					found = 1
					break
			
			recent = cls.cache[index+1:] if found else cls.cache[0:]

			if len(recent) > 0:
				callback(recent)
				return

		cls.waiters.add(callback)


	def cancel_wait(self, callback):
		cls = MessageMixin
		cls.waiters.remove(callback)

	def new_messages(self, messages):
		cls = MessageMixin

		print len(cls.waiters)

		for callback in cls.waiters:
			try:
				print json.dumps( messages )
				callback(messages)
			except Exception, exception:
				print exception
		
		cls.waiters = set()
		cls.cache.extend(messages)
		if len(cls.cache) > cls.cache_size:
			cls.cache = cls.cache[-cls.cache_size:]


class UpdateHandler(tornado.web.RequestHandler, MessageMixin):

	@tornado.web.asynchronous
	def post(self):
		cursor = self.get_argument("cursor", None)
		
		if not cursor: return

		if cursor == "0":
			self.wait_for_messages(self.on_new_messages)
		else:
			self.wait_for_messages(self.on_new_messages, cursor)

	def on_new_messages(self, messages):
		if self.request.connection.stream.closed():
			return

		ret = {"res": messages}

		self.finish( json.dumps(ret) )

	def on_connection_close(self):
		self.cancel_wait(self.on_new_messages)
		print "connection closed"



class NewMessageHandler(tornado.web.RequestHandler, MessageMixin):
	def post(self):
		msg = self.get_argument("msg", None)
		
		if not msg: return

		message = {
			"id": str(uuid.uuid4()),
			"body": msg
		}

		self.write( json.dumps(message) )
		self.new_messages( [message] )












