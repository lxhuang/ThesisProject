#!/usr/bin/env python
from __future__ import division
import tornado.httpserver
import tornado.web
import tornado.database
import json

class Type:
	CODERLIST   = 0
	VIDEOLIST   = 1
	DATABYVIDEO = 2
	DATABYCODER = 3
	CODERPSI    = 4

# Personality Dimension
class PD:
	EXTRO = 1
	AGREE = 2
	CONSCIENTIOUS = 3
	NEUROTICISM = 4
	OPEN = 5
	SELFCONSCIOUS = 6
	OTHERFOCUS = 7
	SHY = 8
	SELFMONITOR = 9

class MainHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def aggregate(self, ts_set, video_len):
		res = [0] * int( round(video_len/100) )

		for ts in ts_set:
			for t in ts:
				beg = (t-500) if (t-500) > 0 else 0
				end = (t+500) if (t+500) < video_len else video_len
				beg = int( round(beg/100)-1 )
				end = int( round(end/100)-1 )
				
				for i in range(beg,end+1):
					res[i] = res[i] + 1

		#print sum(res)

		return res

	def measure(self, personality, coder):
		dimension = [
			1,2,3,4,5,1,2,3,4,5,
			1,2,3,4,5,1,2,3,4,5,
			1,2,3,4,5,1,2,3,4,5,
			1,2,3,4,5,1,2,3,4,5,
			5,2,3,5,6,6,6,6,6,6,
			6,6,6,7,7,7,7,7,7,7,
			8,8,8,8,8,8,8,8,8,8,
			8,8,8,8,8,8,8,8,8,8,
			8,8,9,9,9,9,9,9,6,6
		]
		reverse = [
			0,1,0,0,0,1,0,1,1,0,
			0,1,0,0,0,0,0,1,0,0,
			1,0,1,1,0,0,1,0,0,0,
			1,0,0,1,1,0,1,0,0,0,
			1,0,1,0,0,0,0,1,0,0,
			0,0,0,0,0,0,0,0,0,0,
			0,0,1,0,0,1,0,0,1,0,
			0,1,0,0,0,1,0,1,1,0,
			0,0,0,0,0,0,0,0,0,0
		]
		res = [0] * 9
		cnt = [0] * 9
		for i in range(0, len(personality)):
			if( reverse[i] == 0 ):
				res[dimension[i]-1] = res[dimension[i]-1] + int(personality[i])
			else:
				res[dimension[i]-1] = res[dimension[i]-1] + (5-int(personality[i]))
			cnt[dimension[i]-1] = cnt[dimension[i]-1] + 1
		for i in range(0,9):
			res[i] = res[i] / cnt[i]
			coder[str(i+1)] = "%0.3f" % res[i]

	def calculatePSI(self, s):
		r = 0
		for i in range(0,len(s)):
			r = r + int(s[i])
		return r/len(s)


	def get(self):
		self.render("main.html")

	def post(self):
		try:

			t = self.get_argument("type", None)
			vid = self.get_argument("vid", None)
			turkId = self.get_argument("turkId", None)

			if not t:
				return None

			t = int(t)
			if t == Type.CODERLIST:
				coders = self.db.query("SELECT distinct turkID FROM verify")

				for coder in coders:
					p = self.db.get("SELECT * FROM personality WHERE turkID = %s", coder["turkID"])
					coder["gender"] = p["sex"][0]
					coder["age"] = p["age"]
					self.measure(p["personality"], coder)

				self.write( json.dumps( coders ) )
			
			elif t == Type.VIDEOLIST:
				videos = self.db.query("SELECT distinct vid FROM psi")
				self.write( json.dumps( videos ) )
			
			elif t == Type.DATABYVIDEO:
				coders = self.db.query("SELECT distinct turkID FROM verify")
				
				# time series data from all coders
				ts_set = []
				# messages sent back to the client
				message = []

				video_len = 99999999

				outliner = 0

				for coder in coders:
					f = self.db.get("SELECT feedback FROM feedback WHERE turkID = %s and video = %s", coder["turkID"], vid)
					f = f["feedback"].split(",")
					
					beg = long( f[0].split(":")[1] )
					end = long( f[-1].split(":")[1] )
					
					if end - beg < video_len: video_len = end - beg

					# time series of this coder
					ts  = []

					for i in range(1,len(f)-1):
						elapse = long(f[i].split(":")[1]) - beg
						if elapse > video_len+1000:
							print vid, "\t", coder["turkID"], "\tis outlier"
							message.append( vid + "," + coder["turkID"] )
							outliner = 1
							break;
						else:
							ts.append( elapse )

					#print coder["turkID"], "=>", ts
					if outliner == 0:
						ts_set.append(ts)
					else:
						outlinter = 0
				
				res = self.aggregate(ts_set, video_len)

				ret = {'outliner': message, 'res': res}

				self.write( json.dumps(ret) )
			
			elif t == Type.DATABYCODER:
				f = self.db.get("SELECT feedback FROM feedback WHERE turkID = %s and video = %s", turkId, vid)
				f = f["feedback"].split(",")

				beg = long( f[0].split(":")[1] )
				end = long( f[-1].split(":")[1] )
				
				ts_set = []

				# time series of this coder
				ts  = []
				for i in range(1,len(f)-1):
					elapse = long(f[i].split(":")[1]) - beg
					ts.append( elapse )

				ts_set.append(ts)

				res = self.aggregate(ts_set, end-beg)
				self.write( json.dumps(res) )

			elif t == Type.CODERPSI:
				coders = self.db.query("SELECT distinct turkID FROM verify")

				for coder in coders:
					res = self.db.get("SELECT psi FROM psi WHERE turkID = %s and vid = %s", coder["turkID"], vid)
					res = res["psi"]
					coder["psi"] = "%0.3f" % self.calculatePSI( res )

				self.write( json.dumps( coders ) )

		except Exception, exception:
			print exception




			