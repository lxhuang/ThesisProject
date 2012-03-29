#!/usr/bin/env python
import math
from batch import Batch

class DisplaySCResult:
	"""
	I run spectral clustering on my workstation using Matlab.
	now I need to investigate the clusters
	"""

	batch = None
	clusters = dict()
	dataroot = ""
	videoId = ""

	def load(self, root, screspath, video):
		cls = DisplaySCResult

		cls.videoId = video
		cls.dataroot = root
		cls.batch = Batch()
		cls.batch.load(root)

		fhandler = open(screspath, "r")
		sc_result = fhandler.readlines()
		for item in sc_result:
			[clusterId, coderId] =item.split("\t")
			coderId = coderId.strip()
			if clusterId not in cls.clusters:
				cls.clusters[clusterId] = []
			cls.clusters[clusterId].append(coderId)
		fhandler.close()


	def _writeToFile(self, count, filename):
		fhandler = open(filename, "w")
		for classId in count.iterkeys():
			items = count[classId]
			for item in items:
				fhandler.write( classId + "\t" + str(item) + "\n" )
		fhandler.close()


	def analyze(self, attr, writeToFile=False):
		cls = DisplaySCResult

		print "\nanalyze", attr

		count = dict()
		
		if attr == "loc" or attr == "gender":
			for classId in cls.clusters.iterkeys(): #iterate clusters
				if classId not in count: count[classId] = dict()
				
				items = cls.clusters[classId]
				for item in items:
					val = cls.batch.coder_info_buffer[item][attr]
					if val not in count[classId]:
						count[classId][val] = 1
					else:
						count[classId][val] = count[classId][val] + 1
			
			for classId in count.iterkeys():
				line = classId
				for v in count[classId].iterkeys():
					line = line + "\t" + v + ":" + str(count[classId][v])
				print line
		
		
		elif attr == "psi":
			for classId in cls.clusters.iterkeys():
				if classId not in count: count[classId] = []
				
				items = cls.clusters[classId]
				for item in items:
					psi_file = cls.dataroot + "psi/" + item + "+" + cls.videoId + ".txt"
					fhandler = open(psi_file, "r")
					val = fhandler.readline()
					val = float(val.strip())
					fhandler.close()
					count[classId].append(val)
			
			for classId in count.iterkeys():
				mean = sum(count[classId]) / len(count[classId])
				std = 0
				for v in count[classId]:
					std = std + (v-mean)*(v-mean)
				std = math.sqrt(std / (len(count[classId])-1))
				print classId, "\t", mean, std

		else:
			for classId in cls.clusters.iterkeys():
				if classId not in count: count[classId] = []

				items = cls.clusters[classId]
				for item in items:
					val = cls.batch.coder_info_buffer[item][attr]
					val = float(val)
					count[classId].append(val)

			if writeToFile == True:
				self._writeToFile( count, attr+".txt" )

			for classId in count.iterkeys():
				mean = sum(count[classId]) / len(count[classId])
				std = 0
				for v in count[classId]:
					std = std + (v-mean)*(v-mean)
				std = math.sqrt(std / (len(count[classId])-1))
				print classId, "\t", mean, std


if __name__ == "__main__":
	app = DisplaySCResult()
	app.load("/Users/lixinghu/Documents/projects/ThesisProject/analysis/data/", "sc_result.txt", "4M8tfXK8Y1Y")
	
	app.analyze("loc")
	app.analyze("gender")
	app.analyze("psi")
	app.analyze("extroversion", True)
	app.analyze("agreeableness", True)
	app.analyze("conscientiousness")
	app.analyze("neuroticism")
	app.analyze("openness")
	app.analyze("selfconsciousness")
	app.analyze("otherfocusscale")
	app.analyze("shyness")
	app.analyze("selfmonitor")


