#!/usr/bin/env python
from __future__ import division
from batch import Batch
import os

class BatchIVA:
	coder_set = set()
	video_set = set()

	video_info_buffer = dict()
	video_length = dict()
	feedback_folder = None

	coder_backchannel_num = dict()
	
	def load(self, root):
		cls = BatchIVA
		cls.feedback_folder = root

		fhandle = open(root+"videoLen.txt", "r")
		lines = fhandle.readlines()
		fhandle.close()
		for line in lines:
			[videoName, length] = line.strip().split("\t")
			cls.video_length[videoName] = float(length)/1000

		for filename in os.listdir(root+"feedback"):
			(name, extension) = os.path.splitext(filename)
			if extension == ".txt":
				[coder, video] = name.split("+")
				cls.coder_set.add(coder)
				cls.video_set.add(video)

	
	def loadFeature(self, path):
		cls = BatchIVA

		for filename in os.listdir(path+"feature"):
			(name, extension) = os.path.splitext(filename)
			if extension == ".txt":
				cls.video_info_buffer[name] = dict()

			#	fhandler = open( os.path.join(path, "feature/"+filename), "r" )
				fhandler = open( os.path.join(path, "newfeature/"+filename), "r" )
				info = fhandler.readlines()
				fhandler.close()

				for i in info:
					[feature_name, feature_value] = i.split("|")
					# get rid of Aizula feature
				#	if feature_name in ['VowelVolume', 'Utterence', 'Lowness', 'Downslope', 'EnergyFastEdge', 'EnergyEdge']:
				#		continue
					# get rid of 2-gram features
					if len( feature_name.strip().split(" ") ) == 2: continue

					index = 0
					feature_value = feature_value.strip().split(" ")
					cls.video_info_buffer[name][feature_name] = []
					while index < len(feature_value):
						cls.video_info_buffer[name][feature_name].append( [ float(feature_value[index])*1000, float(feature_value[index+1])*1000 ] )
						index = index + 2

	
	def aggregate(self, video, aggregated):
		cls = BatchIVA

		batch = Batch()

		ts_set = []
		coder_dat_buf = dict()
		coder_dat_len = dict()
		videoL = 999999999999L

		for c in cls.coder_set:
			name = "+".join([c, video])
			filename = os.path.join(cls.feedback_folder, "feedback/"+name+".txt")
			if not os.path.exists(filename):
				print filename, "not exists"
				continue
			feedback = []
			videoLen = batch._processFeedbackFile( filename, feedback )
			coder_dat_buf[name] = feedback
			coder_dat_len[name] = videoLen
			
			if videoLen < videoL: videoL = videoLen
		
		try:
			for k in coder_dat_buf.iterkeys():
				v = coder_dat_buf[k]
				if len(v) == 0:
					pass
				elif coder_dat_len[k] > videoL + 1500:
					print coder_dat_len[k], ";", videoL, " [aggregate] ", video, k, " is outlier"
				else:
					ts_set.append(v)
		except Exception, exception:
			raise exception

		_aggregated = batch._aggregate(ts_set, videoL)
		for _item in _aggregated:
			aggregated.append(_item)
		return videoL

	
	def extractFromAggregated(self, aggregated):
		batch = Batch()

		total = sum(aggregated)
		entropy = batch._entropy(aggregated)
		return [total, entropy]

	
	def process(self, video):
		aggregated = []
		videoL = self.aggregate(video, aggregated)
		videoL = videoL / 1000
		[total, entropy] = self.extractFromAggregated(aggregated)
		frequency = total / videoL
		print video + "\t" + str(frequency) + "\t" + str(entropy)

	
	def processAll(self):
		cls = BatchIVA
		for v in cls.video_set:
			self.process(v)
	
	
	def _matchWithFeature(self, c, v, coder_feature, window=1000):
		cls   = BatchIVA
		batch = Batch()

		name = "+".join( [c, v] )
		filename = os.path.join( cls.feedback_folder, "feedback/"+name+".txt" )
		if not os.path.exists(filename):
			print filename, "not exists"
			return

		feedback = []
		videoLen = batch._processFeedbackFile(filename, feedback)

		if c not in cls.coder_backchannel_num:
			cls.coder_backchannel_num[c] = len(feedback)
		else:
			cls.coder_backchannel_num[c] = cls.coder_backchannel_num[c] + len(feedback)

		try:
			for feature_name in cls.video_info_buffer[v].iterkeys():
				feature_values = cls.video_info_buffer[v][feature_name]
				for feature_value in feature_values:
					for f in feedback:
						if feature_value[0] <= f and f <= feature_value[1]+window:
							if feature_name in coder_feature:
								coder_feature[feature_name] = coder_feature[feature_name]+1
							else:
								coder_feature[feature_name] = 1
		except Exception, exception:
			print exception


	def matchWithFeature(self, window=1000):
		cls = BatchIVA

		coder_feature = dict()
		for v in cls.video_set:
			for c in cls.coder_set:
				if c not in coder_feature:
					coder_feature[c] = dict()
				self._matchWithFeature(c, v, coder_feature[c], window)
			print "matchWithFeature processed => ", v

		
		# display
		for c in cls.coder_set:
			res = []
			for k in coder_feature[c].iterkeys():
				val = coder_feature[c][k]
				
				total = 0
				for v in cls.video_info_buffer.iterkeys():
					if k in cls.video_info_buffer[v]:
						total = total + len(cls.video_info_buffer[v][k])

				bc_num = cls.coder_backchannel_num[c]

				prec = val/total
				reca = val/bc_num

				f = 2*prec*reca/(prec+reca)
				if f > 1:
					print prec
					print reca

				res.append( [k, f] )
			res = sorted( res, key=lambda ele: -ele[1] )

			print c, cls.coder_backchannel_num[c]
			for r in res[0:30]:
				print "\t" + str(r[0]) + "\t" + str(r[1])


if __name__ == "__main__":
	app = BatchIVA();
	app.load("/Users/lixinghu/Documents/projects/MTurk/processIVADat/")
	app.loadFeature("/Users/lixinghu/Documents/projects/MTurk/processIVADat/")
	app.matchWithFeature(500)
	app.processAll()







