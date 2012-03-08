#!/usr/bin/env python
import tornado.httpserver
import tornado.web
import tornado.database
import os.path

class AnalysisHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

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
		attr = [
			"extroversion",
			"agreeableness",
			"conscientiousness",
			"neuroticism",
			"openness",
			"selfconsciousness",
			"otherfocusscale",
			"shyness",
			"selfmonitor"
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
			coder[attr[i]] = "%0.3f" % res[i]

	def calculatePSI(self, s):
		r = 0
		for i in range(0,len(s)):
			r = r + int(s[i])
		return r/len(s)


	def retrieveData(self):
		try:
			
			root = os.path.join(os.path.dirname(__file__), "data")
			
			lineno = 1
			feedback = self.db.query("SELECT feedback.turkID, feedback.video, feedback.feedback FROM verify "
										"left join feedback on feedback.turkID = verify.turkID order by feedback.turkID")
			for f in feedback:
				vid = f["video"]
				tid = f["turkID"]
				dat = f["feedback"]

				filename = root + "/feedback/" + tid + "_" + vid + ".txt"

				if not os.path.exists(filename):
					print "[", lineno, "] writing to ", filename
					fhandle = open(filename, "w")
					fhandle.write( dat )
					fhandle.close()
				else:
					print "[", lineno, "] ", filename, " exists"
				lineno = lineno + 1

			
			lineno = 1
			personality = self.db.query("SELECT personality.turkID, personality.age, personality.sex, personality.personality, personality.location FROM verify "
										"left join personality on personality.turkID = verify.turkID order by personality.turkID")
			for p in personality:
				tid = p["turkID"]
				age = p["age"]
				sex = p["sex"]
				psn = p["personality"]
				loc = p["location"]

				filename = root + "/personality/" + tid + ".txt"

				if not os.path.exists(filename):
					print "[", lineno, "] writing to ", filename
					fhandle = open(filename, "w")
					fhandle.write("age\t"+str(age))
					fhandle.write("gender\t"+sex)
					fhandle.write("loc\t"+str(loc))

					coder = {}
					self.measure(psn, coder)

					for k in coder.iterkeys():
						fhandle.write(k+"\t"+str(coder[k]))
					
					fhandle.close()
				else:
					print "[", lineno, "] ", filename, " exists"
				lineno = lineno + 1


			lineno = 1			
			psi = self.db.query("SELECT psi.turkID, psi.vid, psi.psi FROM verify left join psi on psi.turkID = verify.turkID order by psi.turkID")
			for psiitem in psi:
				tid = psiitem["turkID"]
				vid = psiitem["vid"]
				val = psiitem["psi"]
				val = self.calculatePSI(val)
				
				filename = root + "/psi/" + tid + "_" + vid + ".txt"
				
				if not os.path.exists(filename):
					print "[", lineno, "] writing to ", filename
					fhandle = open(filename, "w")
					fhandle.write(str(val))
					fhandle.close()
				else:
					print "[", lineno, "] ", filename, " exists"
				lineno = lineno + 1

		except Exception, exception:
			print exception


	def post(self):
		type = self.get_argument("type")
		if type == "retrieve":
			self.retrieveData()
			self.write("{\"success\": \"1\"}")

		

	def get(self):
		self.render("analysis.html")













