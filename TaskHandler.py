#!/usr/bin/env python

import tornado.httpserver
import tornado.web
import tornado.database

import random

#164,162,159,157,155,154,153,149,148,147,146,144,141,139,134,130,115,112,69,60,53,50,47,39,
#video_string = "l_S-RM-8l9w,qrHqKOkHNME,xAZ3-QGMWjo,UcaYbyw8MZo,f_U76yiaexg,bfBMc4RDafg,4M8tfXK8Y1Y,f7e91xGHQJ8"
#video_string = "BJTqFwhD3Zo,FitPohYSHFE,HD7_rI1YVV0,jXjKatmQCnE,2XIaHNhjlPs,PqSaLwyuNAE,Wedwm36_9tk,NBCqKx10Nic"
video_string = "ApTBjM9EJT0,KaIRz8NTkUY,XxMY94nYZaM,m-rZwZAqjqQ,DSbIF3NMRT8,Axbv9YJcVXs,HIofrWKm2YU,SRXNmraVel0"

class TaskHandler(tornado.web.RequestHandler):

	@property
	def db(self):
		return self.application.db

	def post(self):
		turkId = self.get_argument("tid", None)
		action = self.get_argument("act", None)
		if not turkId:
			return None

		# check whether the ID existed or not
		# if not, assign new tasks to him; otherwise, return the top one
		user = self.db.get( "SELECT * FROM task WHERE turkID = %s", turkId )
		if not user:
			try:
				rnd = video_string.split(',')
				random.seed()
				random.shuffle(rnd)

				rnd_str = ','.join(rnd)
				res = self.db.execute(
					"INSERT INTO task (turkID, task) VALUES (%s, %s)", turkId, rnd_str
				)

				self.write("{\"v\":\"" + rnd[0] + "\"}")
			except Exception, exception:
				print exception
				
		else:
			if not action: #request
				try:
					tsk = self.db.get( "SELECT * FROM task WHERE turkID = %s", turkId )
					remains = tsk["task"]
					if remains == "":
						self.write("{\"v\": \"-1\"}")
					else:
						remains = remains.split(',')
						self.write("{\"v\":\"" + remains[0] + "\"}")
				except Exception, exception:
					return None
			
			else: #pop up the video
				tsk = self.db.get( "SELECT * FROM task WHERE turkID = %s", turkId )
				remains = tsk["task"]
				remains = remains.split(",")
				remains.pop(0)
				remains = ','.join(remains)
				try:
					self.db.execute("UPDATE task SET task = %s WHERE turkID = %s", remains, turkId)
					self.write("{\"res\":\"success\"}")
				except Exception, exception:
					print exception.args
					print exception
					self.write("{\"res\":\"fail\"}")
					return None
