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
	DATABYCODERS= 5

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
		t = self.get_argument("type", None)
		vid = self.get_argument("vid", None)
		turkId = self.get_argument("turkId", None)
		turkIds = self.get_argument("turkIds", None)

		if not t: return None

		t = int(t)
		if t == Type.CODERLIST:
			try:
				coders = self.db.query("SELECT distinct turkID FROM verify")

				for coder in coders:
					p = self.db.get("SELECT * FROM personality WHERE turkID = %s", coder["turkID"])
					coder["gender"] = p["sex"][0]
					coder["age"] = p["age"]
					coder["loc"] = p["location"]
					self.measure(p["personality"], coder)

				self.write( json.dumps( coders ) )
			except Exception, exception:
				print "Type.CODERLIST=>", exception
			
		elif t == Type.VIDEOLIST:
			try:
				videos = self.db.query("SELECT distinct vid FROM psi")
				self.write( json.dumps( videos ) )
			except Exception, exception:
				print "Type.VIDEOLIST=>", exception
			
		elif t == Type.DATABYVIDEO:
			try:
				#coders = self.db.query("SELECT distinct turkID FROM verify")
				coders = self.db.query("SELECT distinct turkID FROM feedback where video = %s and turkID in (SELECT distinct turkID FROM verify)", vid)

				ts_set = []
				
				# messages sent back to the client
				message = []
				ret_coder = []
				outlier = 0

				video_len = 99999999
				for coder in coders:
					# time series of this coder
					ts  = []

					f = self.db.get("SELECT feedback FROM feedback WHERE turkID = %s and video = %s", coder["turkID"], vid)
					if not f: continue

					f = f["feedback"].split(",")

					print coder["turkID"], vid
					ret_coder.append(coder["turkID"])
					
					beg_index = 0
					while beg_index < len(f):
						if f[beg_index].split(":")[0] == "s":
							break
						beg_index = beg_index+1
					
					end_index = len(f)-1
					while end_index >= 0:
						if f[end_index].split(":")[0] == "p":
							break
						end_index = end_index-1

					beg = long( f[beg_index].split(":")[1] )
					end = long( f[end_index].split(":")[1] )
					
					if end - beg < video_len: video_len = end - beg

					space = 0
					index = beg_index + 1
					while index < end_index:
						if f[index].split(":")[0] == "pp":
							if f[index+1].split(":")[0] == "c":
								space = space + long(f[index+1].split(":")[1]) - long(f[index].split(":")[1])
								index = index + 2
							else:
								if index < end_index-1:
									print coder["turkID"], "\t", vid, " [pp,c] does not match"
								index = index + 1
						elif f[index].split(":")[0] == "b":
							elapse = long(f[index].split(":")[1]) - beg - space
							if elapse > video_len + 1500:
								print vid, "\t", coder["turkID"], " is outlier"
								message.append( vid + "," + coder["turkID"] )
								outlier = 1
								break
							else:
								ts.append(elapse)
								index = index + 1
						else:
							print coder["turkID"], vid, f[index], " => weird format"
							index = index + 1

					if outlier == 0:
						ts_set.append(ts)
					else:
						outlier = 0
				
				res = self.aggregate(ts_set, video_len)
				ret = {'outlier': message, 'res': res, 'coder': ret_coder}
				self.write( json.dumps(ret) )
			except Exception, exception:
				print "Type.DATABYVIDEO=>", exception
			
		elif t == Type.DATABYCODER:
			try:
				ts_set = []
				ts  = []

				f = self.db.get("SELECT feedback FROM feedback WHERE turkID = %s and video = %s", turkId, vid)
				if not f:
					self.write( json.dumps(ts) )
					return

				f = f["feedback"].split(",")
				beg_index = 0
				while beg_index < len(f):
					if f[beg_index].split(":")[0] == "s":
						break
					beg_index = beg_index+1
					
				end_index = len(f)-1
				while end_index >= 0:
					if f[end_index].split(":")[0] == "p":
						break
					end_index = end_index-1
				
				beg = long( f[beg_index].split(":")[1] )
				end = long( f[end_index].split(":")[1] )
				
				space = 0
				index = beg_index + 1
				while index < end_index:
					if f[index].split(":")[0] == "pp":
						if f[index+1].split(":")[0] == "c":
							space = space + long(f[index+1].split(":")[1]) - long(f[index].split(":")[1])
							index = index + 2
						else:
							if index < end_index-1:
								print turkId, "\t", vid, " [pp,c] does not match"
							index = index + 1
					elif f[index].split(":")[0] == "b":
						elapse = long(f[index].split(":")[1]) - beg - space
						ts.append(elapse)
						index = index + 1
					else:
						print turkId, vid, f[index], " =>weird format"
						index = index + 1

				ts_set.append(ts)

				res = self.aggregate(ts_set, end-beg)
				self.write( json.dumps(res) )
			except Exception, exception:
				print "Type.DATABYCODER=>", exception

		elif t == Type.CODERPSI:
			try:
				#coders = self.db.query("SELECT distinct turkID FROM verify")
				coders = self.db.query("SELECT distinct turkID FROM feedback where video = %s and turkID in (SELECT distinct turkID FROM verify)", vid)

				for coder in coders:
					print "[CODERPSI]=>", coder["turkID"], vid
					res = self.db.get("SELECT psi FROM psi WHERE turkID = %s and vid = %s", coder["turkID"], vid)
					res = res["psi"]
					coder["psi"] = "%0.3f" % self.calculatePSI( res )

				self.write( json.dumps( coders ) )
			except Exception, exception:
				print "Type.CODERPSI=>", exception

		elif t == Type.DATABYCODERS:
			try:
				ts_set = []
				outlier= 0
				video_len = 99999999

				coders = turkIds.split("|")
				for coder in coders:
					# time series of this coder
					ts  = []

					f = self.db.get("SELECT feedback FROM feedback WHERE turkID = %s and video = %s", coder, vid)
					if not f: continue

					f = f["feedback"].split(",")
					
					print "cluster analysis=>", coder

					beg_index = 0
					while beg_index < len(f):
						if f[beg_index].split(":")[0] == "s":
							break
						beg_index = beg_index+1
					
					end_index = len(f)-1
					while end_index >= 0:
						if f[end_index].split(":")[0] == "p":
							break
						end_index = end_index-1

					beg = long( f[beg_index].split(":")[1] )
					end = long( f[end_index].split(":")[1] )
					
					if end - beg < video_len: video_len = end - beg

					space = 0
					index = beg_index + 1
					while index < end_index:
						if f[index].split(":")[0] == "pp":
							if f[index+1].split(":")[0] == "c":
								space = space + long(f[index+1].split(":")[1]) - long(f[index].split(":")[1])
								index = index + 2
							else:
								if index < end_index-1:
									print coder, "\t", vid, " [pp,c] does not match"
								index = index + 1
						elif f[index].split(":")[0] == "b":
							elapse = long(f[index].split(":")[1]) - beg - space
							if elapse > video_len + 1500:
								print vid, "\t", coder, "\tis outlier"
								outlier = 1
								break
							else:
								ts.append(elapse)
								index = index + 1
						else:
							print coder["turkID"], vid, f[index], " =>weird format"
							index = index + 1

					if outlier == 0:
						ts_set.append(ts)
					else:
						outlier = 0
				
				if video_len == 99999999:
					ret = {'res': []}
					self.write( json.dumps(ret) )
				else:
					res = self.aggregate(ts_set, video_len)
					ret = {'res': res}
					self.write( json.dumps(ret) )
			except Exception, exception:
				print "Type.DATABYCODERS=>", exception


			