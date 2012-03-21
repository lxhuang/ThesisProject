#!/usr/bin/env python
from __future__ import division
from batch import Batch
import random
import uuid
import math

class ClusterCoder:

	batch = None
	coder_data = dict()
	dist_table = dict()

	def load(self, root):
		try:
			cls = ClusterCoder

			cls.batch = Batch()
			cls.batch.load(root)

			for c in cls.batch.coder_set:
				cls.coder_data[c] = dict()
				for v in cls.batch.video_set:
					feedback = []
					name = "+".join( [c, v] )
					cls.batch._processFeedbackFile(root+"feedback/"+name+".txt", feedback)
					if len(feedback) != 0:
						cls.coder_data[c][v] = feedback
		except Exception, exception:
			print "load => ", exception

	
	def _prepareData(self, videoId, data):
		try:
			cls = ClusterCoder
			
			for c in cls.coder_data.iterkeys():
				if videoId in cls.coder_data[c]:
					feedback = cls.coder_data[c][videoId]
					data_point = {
						"classId": -1,
						"coder": c,
						"dat": feedback
					}
					data.append( data_point )
			print "total sample size: ", len(data)
			
			print "computing the distance table"
			
			fhandler = open("dist_table.txt", "w")
			fhandler1 = open("coder.txt", "w")
			for d1 in data:
				
				line = ""
				for d2 in data:
					key = d1["coder"] + "+" + d2["coder"]
					cls.dist_table[key] = self._distance( d1, d2 )
					line = line + str( cls.dist_table[key] ) + "\t"
				
				fhandler.write(line+"\n")
				fhandler1.write(d1["coder"]+"\n")
			
			fhandler.close()
			fhandler1.close()

		except Exception, exception:
			print "_prepareData => ", exception

	
	def _initializeCentroid(self, data, num, centroids):
		print "initialize centroids:"
		try:
			cls = ClusterCoder

			index = range(0, len(data))
			
			# randomize
			s = uuid.uuid4()
			random.seed(s)
			random.shuffle( index )

			for i in range(num):
				j = int( round(len(data)/num*i) )
				data[index[j]]["classId"] = i
				centroids.append( data[index[j]] )

				print "centroid of class ", i, data[index[j]]["coder"]
		
		except Exception, exception:
			print "_initializeCentroid => ", exception

	
	def _assignToClusters(self, data, centroids):
		try:
			print "assign to clusters"

			count = dict()
			for c in centroids:
				count[c["classId"]] = 0

			measure = 0
			for d in data:
				min_distance = 9999999999
				assigned_cls = -1
				
				for c in centroids:
					_dist = self._distance( d, c )
					if min_distance > _dist:
						min_distance = _dist
						assigned_cls = c["classId"]
				
				measure = measure + min_distance
				d["classId"] = assigned_cls
				count[assigned_cls] = count[assigned_cls] + 1

			for k in count.iterkeys():
				print "size of classId ", k, " => ", count[k]
			print "total distance:", measure
		
		except Exception, exception:
			print "_assignToClusters => ", exception


	def _calculateNewCentroids(self, data, centroids):
		try:
			print "\ncalculate new centroids:"

			del centroids[:]

			_clusters = dict()
			for d in data:
				classId = d["classId"]
				if classId not in _clusters:
					_clusters[classId] = []
				_clusters[classId].append(d)

			#measure = 0
			
			for c in _clusters.iterkeys():
				buddy = _clusters[c]

				new_centroid = None
				min_distance = 99999999
				for i in range(0, len(buddy)):
					_dist = 0
					for j in range(0, len(buddy)):
						_dist = _dist + self._distance( buddy[i], buddy[j] )
					if _dist < min_distance:
						min_distance = _dist
						new_centroid = buddy[i]
				
				centroids.append(new_centroid)
				#measure = measure + min_distance
				print "centroid of class ", c, new_centroid["coder"]

			#print "total distance: ", measure
			#return measure
		
		except Exception, exception:
			print "_calculateNewCentroids => ", exception
	

	def _output(self, data, attr):
		cls = ClusterCoder
		
		measure = dict()

		for d in data:
			print d["classId"], "\t", d["coder"], "\t", cls.batch.coder_info_buffer[d["coder"]][attr]
			if d["classId"] not in measure:
				measure[d["classId"]] = []
			measure[d["classId"]].append( float(cls.batch.coder_info_buffer[d["coder"]][attr]) )
		
		print "distribution of ", attr
		for k in measure:
			total = 0
			mean = sum(measure[k])/len(measure[k])
			for val in measure[k]:
				total = total + (val-mean)*(val-mean)
			std = math.sqrt( total / (len(measure[k])-1) )
			print "\tclassId: ", k, mean, std

	
	def _buildTS(self, feedback, ts):
		try:
			for f in feedback:
				beg = (f-500)
				end = (f+500)
				beg = int( round(beg/100) )
				end = int( round(end/100) )
				for i in range(beg, end+1):
					if 0<=i and i<len(ts):
						ts[i] = ts[i] + 1
		except Exception, exception:
			print "_buildTS", exception

	
	def _distance(self, c1, c2, win=1000):
		try:
			cls = ClusterCoder

			key = c1["coder"] + "+" + c2["coder"]
			if key in cls.dist_table:
				return cls.dist_table[key]

			score = 0
			adat = c1["dat"]
			bdat = c2["dat"]
			alen = len(adat)
			blen = len(bdat)

			#print adat
			#print bdat

			for i in range(alen):
				for j in range(blen):
					if abs(adat[i]-bdat[j]) < win:
						score = score + 1
					if bdat[j] > adat[i] + win:
						break
			
			return -(2*score) / (alen+blen)
		except Exception, exception:
			print "_distance", exception


	def testDistance(self, videoId, coderId1, coderId2):
		cls = ClusterCoder
			
		feedback1 = cls.coder_data[coderId1][videoId]
		feedback2 = cls.coder_data[coderId2][videoId]
		
		c1 = {"coder": coderId1, "dat": feedback1}
		c2 = {"coder": coderId2, "dat": feedback2}

		print self._distance(c1, c2)


	def cluster(self, videoId, num, attr):
		cls = ClusterCoder

		data = []
		centroids = []
		
		self._prepareData(videoId, data)
		self._initializeCentroid( data, num, centroids )
		
		times = 5
		while times > 0:
			self._assignToClusters( data, centroids )
			self._calculateNewCentroids( data, centroids )
			times = times - 1

		self._output( data, attr )


if __name__ == "__main__":
	app = ClusterCoder()
	app.load("/Users/lixinghu/Documents/projects/ThesisProject/analysis/data/")
	app.cluster("UcaYbyw8MZo", 2, "agreeableness")
#	app.testDistance("l_S-RM-8l9w", "A1Y4LA3VWRF6S6", "A3AVZHEIMSKFD3")


