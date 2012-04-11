#!/usr/bin/env python
from __future__ import division
import os
from peak import Peak
from batch import Batch

class CompareHighPkWithLowPk:

	peak = None
	video_info_buffer = {}

	def load(self, root):
		
		cls = CompareHighPkWithLowPk
		cls.peak = Peak()
		cls.peak.load(root)

		feature_path = os.path.join(root, "features")
		
		for filename in os.listdir( feature_path ):
			(name, extension) = os.path.splitext( filename )
			
			if extension == ".txt":
				fhandler = open( os.path.join(feature_path, filename), "r" )
				cls.video_info_buffer[name] = dict()
				info = fhandler.readlines()
				fhandler.close()

				for i in info:
					[feature_name, feature_value] = i.strip().split("|")

					# get rid of Aizula feature
					if feature_name in ['VowelVolume', 'Utterence', 'Lowness', 'Downslope', 'EnergyFastEdge', 'EnergyEdge']:
						continue

					# get rid of 2-gram features
					if len( feature_name.strip().split(" ") ) == 2:
						continue

					index = 0
					feature_value = feature_value.strip().split(" ")
					cls.video_info_buffer[name][feature_name] = []
					while index < len(feature_value):
						cls.video_info_buffer[name][feature_name].append( [ float(feature_value[index])*1000, float(feature_value[index+1])*1000 ] )
						index = index + 2

	
	def getPeaksForVideo(self, videoId):
		aggregated = []

		cls = CompareHighPkWithLowPk
		cls.peak.batch._getDataOfVideo(videoId, aggregated)

		allpeaks = cls.peak._process(aggregated, 350)
		return allpeaks


	def matchWithFeature(self, videoId, allpeaks, tail, window):
		cls = CompareHighPkWithLowPk

		allpeaks = sorted(allpeaks, key=lambda ele: ele[1])

		if tail > len(allpeaks)/2:
			raise Exception("tail exceeds half")

		feature_set = cls.video_info_buffer[videoId]

		lo_feature_set = dict()
		hi_feature_set = dict()

		for i in range(0, tail):
			lo_t = (allpeaks[i][0]/10)*1000
			hi_t = (allpeaks[-i-1][0]/10)*1000

		#	print lo_t
		#	print hi_t

			for feature_name in feature_set.iterkeys():
				feature_values = feature_set[feature_name]
				
				for feature_value in feature_values:
					if (feature_value[0] <= lo_t) and (lo_t <= feature_value[1]+window):
						if feature_name in lo_feature_set:
							lo_feature_set[feature_name] = lo_feature_set[feature_name] + 1
						else:
							lo_feature_set[feature_name] = 1
						if feature_name == "\"Pause\"":
							print "low peak pause length => ", (feature_value[1]-feature_value[0])
						break
				
				for feature_value in feature_values:
					if (feature_value[0] <= hi_t) and (hi_t <= feature_value[1]+window):
						if feature_name in hi_feature_set:
							hi_feature_set[feature_name] = hi_feature_set[feature_name] + 1
						else:
							hi_feature_set[feature_name] = 1
						if feature_name == "\"Pause\"":
							print "high peak pause length => ", (feature_value[1]-feature_value[0])
						break
			
		#	print lo_feature_set
		#	print hi_feature_set

		return [lo_feature_set, hi_feature_set]

	
	def _displayFeatureSet(self, feature_set):
		for feature in feature_set.iterkeys():
			print feature, "\t", feature_set[feature]

	
	def processVideo(self, videoId, tail, window):
		print "================"
		print "process ", videoId
		allpeaks = self.getPeaksForVideo(videoId)
		feature_set = self.matchWithFeature(videoId, allpeaks, tail, window)
		
		print "\nlow peak features"
#		self._displayFeatureSet(feature_set[0])
		print feature_set[0]
		
		print "\nhigh peak features"
#		self._displayFeatureSet(feature_set[1])
		print feature_set[1]

	
	def processVideos(self, tail, window):
		cls = CompareHighPkWithLowPk
		for v in cls.peak.batch.video_set:
			self.processVideo(v, tail, window)


if __name__ == "__main__":
	app = CompareHighPkWithLowPk()
	app.load("/Users/lixinghu/Documents/projects/ThesisProject/analysis/data/")
	app.processVideos(8, 3.0)
#	app.processVideo("l_S-RM-8l9w", 6, 1.5)




