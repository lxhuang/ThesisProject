#!/usr/bin/env python
from __future__ import division
from batch import Batch
import os
import math
import json

class DiveFeature:
	"""
	dive into the speaker's feature
	in each video, what kind of speaker features is likely to trigger bc
	for each coder, what kind of speaker features do they focus on
	"""

	data_root = ""
	coder_set = set()
	video_set = set()

	coder_info_buffer = dict()
	video_info_buffer = dict()

	
	def load(self, root):
		try:
			cls = DiveFeature

			cls.data_root = root

			
			feedback_path = os.path.join(cls.data_root, "feedback")
			for filename in os.listdir( feedback_path ):
				(name, extension) = os.path.splitext( filename )
				if extension == ".txt":
					[turkId, videoId] = name.split("+")
					cls.coder_set.add( turkId )
					cls.video_set.add( videoId )

			
			personality_path = os.path.join(cls.data_root, "personality")
			for filename in os.listdir( personality_path ):
				(name, extension) = os.path.splitext( filename )
				if extension == ".txt":
					cls.coder_info_buffer[name] = dict()

					fhandler = open( os.path.join(personality_path, filename), "r" )
					info = fhandler.readlines()
					fhandler.close()

					for i in info:
						[k, v] = i.split("\t")
						cls.coder_info_buffer[name][k] = v

			
			feature_path = os.path.join(cls.data_root, "features")
			for filename in os.listdir( feature_path ):
				(name, extension) = os.path.splitext( filename )
				if extension == ".txt":
					cls.video_info_buffer[name] = dict()

					fhandler = open( os.path.join(feature_path, filename), "r" )
					info = fhandler.readlines()
					fhandler.close()

					for i in info:
						[feature_name, feature_value] = i.split("|")

						# get rid of Aizula feature
						if feature_name in ['VowelVolume', 'Utterence', 'Lowness', 'Downslope', 'EnergyFastEdge', 'EnergyEdge']:
							continue

						# get rid of 2-gram features
						if len( feature_name.strip().split(" ") ) == 2:
							continue

						feature_value = feature_value.strip().split(" ")
						index = 0

						cls.video_info_buffer[name][feature_name] = []
						while index < len(feature_value):
							cls.video_info_buffer[name][feature_name].append( [ float(feature_value[index])*1000, float(feature_value[index+1])*1000 ] )
							index = index + 2

		except Exception, exception:
			print "load => ", exception

	
	# window is in milliseconds.
	def _matchWithFeature(self, coderId, videoId, coder_feature, video_feature, window=1000):
		try:
			cls = DiveFeature

			feedback = []
			
			name = "+".join( [coderId, videoId] )
			filename = os.path.join( cls.data_root, "feedback/" + name + ".txt" )

			
			batch = Batch()
			videoLen = batch._processFeedbackFile(filename, feedback)

			try:
				for feature_name in cls.video_info_buffer[videoId].iterkeys():

					feature_values = cls.video_info_buffer[videoId][feature_name]
				
					for feature_value in feature_values:
						for f in feedback:
							if feature_value[0] <= f and f <= feature_value[1]+window:
								
								if feature_name in video_feature:
									video_feature[feature_name] = video_feature[feature_name] + 1
								else:
									video_feature[feature_name] = 1

								if feature_name in coder_feature:
									coder_feature[feature_name] = coder_feature[feature_name] + 1
								else:
									coder_feature[feature_name] = 1
			
			except Exception, exception:
				print exception

		except Exception, exception:
			print "_matchWithFeature => ", exception

	
	def matchWithFeature(self):
		try:
			cls = DiveFeature

			video_feature = dict()
			coder_feature = dict()	

			for v in cls.video_set:
			
				video_feature[v] = dict()

				for c in cls.coder_set:
				
					if c not in coder_feature: coder_feature[c] = dict()

					self._matchWithFeature( c, v, coder_feature[c], video_feature[v] )

				print "[matchWithFeature] => processed ", v

			
			for v in cls.video_set:
				print "{{", v, "}} => "

				res = []
				
				for k in video_feature[v].iterkeys():
					value = video_feature[v][k] / ( len(cls.video_info_buffer[v][k]) * len(cls.coder_set) )
					res.append( [k, value] )

				res = sorted( res, key=lambda ele: ele[1] )

				for r in res: print "\t", r[0], " => ", r[1]

			lineno = 1
			for c in cls.coder_set:
				res = []

				for k in coder_feature[c].iterkeys():
					value = coder_feature[c][k]
					res.append( [k, value] )
					
				res = sorted( res, key=lambda ele: ele[1] )

				line = "[" + str(lineno) + "] " + c + " => "
				lineno = lineno + 1
				
				#for r in res: print r[0], " => ", r[1]

				for r in res[-10:-1]: line = line + "{" + str(r[0]) + "," + str(r[1]) + "} "
				
				#word = "massage"
				#if word in coder_feature[c]:
				#	line = line + str( coder_feature[c][word] )
				#else:
				#	line = line + "0"

				print line
				
		
		except Exception, exception:
			print "matchWithFeature => ", exception


if __name__ == "__main__":
	app = DiveFeature()
	app.load("/Users/lixinghu/Documents/projects/ThesisProject/analysis/data/")
	app.matchWithFeature()




