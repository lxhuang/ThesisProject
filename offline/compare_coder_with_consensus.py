#!/usr/bin/env python
from __future__ import division
from batch import Batch
from peak import Peak
import os
import math
import json

class CompareCoderWithConsensus:

	peak = None
	
	topN = 5

	data_path = None

	
	def load(self, root):
		cls = CompareCoderWithConsensus
		cls.data_path = root
		cls.peak = Peak()
		cls.peak.load(root)

	
	def _getConsensusPeakForVideo(self, videoId, num):
		# num: the number of coders
		aggregated = []

		cls = CompareCoderWithConsensus
		cls.peak.batch._getDataOfVideo(videoId, aggregated)
		peaks = cls.peak._process(aggregated, num)
		return peaks

	
	def _getDataForCoder(self, videoId, coderId):
		cls = CompareCoderWithConsensus

		name = "+".join( [coderId, videoId] )
		if name in cls.peak.batch.outlier_buffer:
			return []
		
		feedback = []
		filename = os.path.join( cls.data_path, "feedback/"+name+".txt" )
		cls.peak.batch._processFeedbackFile( filename, feedback )
		return feedback


	def _compareCoderWithConsensus(self, consensusPeak, individualPeak):
		cls = CompareCoderWithConsensus

		total    = len(individualPeak)
		match    = 0
		common   = 0
		mismatch = 0

		if len(consensusPeak) <= cls.topN: raise Exception("topN is too big")

		consensusPeak = sorted(consensusPeak, key=lambda ele: ele[1])
		
		highAgreement = []
		for i in range(-cls.topN, 0):
			highAgreement.append( consensusPeak[i][0]*100 )
		
		
		consensusTime = []
		for i in range(0, len(consensusPeak)-cls.topN):
			consensusTime.append( consensusPeak[i][0]*100 )

		
		tmp = []
		for tt in individualPeak:
			for t in highAgreement: # high agreement peaks
				if abs(tt-t) < 500:
					common = common + 1
					tmp.append(tt)
					break
		
		for tt in individualPeak:
			if tt in tmp: continue
			
			isMatch = False
			for t in consensusTime:
				if abs(tt-t) < 500:
					match = match + 1
					isMatch = True
					break
			if not isMatch:
				mismatch = mismatch + 1
		
		return [total, match, common, mismatch]



	def compareCoderWithConsensus(self, videoId, coderId):
		individualPeak = self._getDataForCoder(videoId, coderId)
		consensusPeak = self._getConsensusPeakForVideo(videoId, 350)
		
		if len(individualPeak) == 0:
			return []
		else:
			result = self._compareCoderWithConsensus(consensusPeak, individualPeak)
			return result

	
	def getCoderAttribution(self, coderId):
		cls = CompareCoderWithConsensus
		personality = cls.peak.batch.coder_info_buffer[coderId]
		
		attr  = []
		value = []
		
		for k in personality.iterkeys():
			attr.append(k)
			value.append(personality[k])

	#	print "\t".join(attr)
	#	print "\t".join(value)

		return [attr, value]	


	def compareWithConsensus(self, videoId):
		alllines = []

		cls = CompareCoderWithConsensus
		
		for c in cls.peak.batch.coder_set:
			result = self.compareCoderWithConsensus(videoId, c)
			if len(result) == 0:
				print c, "[ignored]"
				continue
			else:
				print c
				attribution = self.getCoderAttribution(c)
				line = [c]
				line.extend( result )
				line.extend( attribution[1] )
			alllines.append( line )
		
		
		for line in alllines:
			textline = ""
			for item in line:
				textline = textline + str(item) + "\t"
			print textline

		return alllines
	
	
	def processAllVideos(self):
		cls = CompareCoderWithConsensus

		for v in cls.peak.batch.video_set:
			res = self.compareWithConsensus(v)



if __name__ == "__main__":
	app = CompareCoderWithConsensus()
	app.load("/Users/lixinghu/Documents/projects/ThesisProject/analysis/data/")
#	app.getCoderAttribution("A1EXDIVIESBKT0")
	app.compareWithConsensus("l_S-RM-8l9w")







