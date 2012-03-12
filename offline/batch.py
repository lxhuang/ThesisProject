#!/usr/bin/env python
from __future__ import division
import os
import math
import json

class MyException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Batch:
	data_root = ""
	coder_set = set()
	video_set = set()	
	
	outlier_buffer = dict()
	coder_info_buffer = dict()

	def load(self, root):
		try:
			cls = Batch

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

					fhandler = open( filename, "r" )
					info = fhandler.readlines()
					fhandler.close()

					for i in info:
						[k, v] = i.split("\t")
						cls.coder_info_buffer[name][k] = v
		
		except Exception, exception:
			print "load => ", exception


	def _aggregate(self, ts_set, video_len):
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

	
	def _entropy(self, ts):
		ent = 0
		s = sum(ts)
		for i in range(0, len(ts)):
			p = ts[i]/s
			if p != 0: ent = ent - p * math.log10(p)
		
		return ent

	
	def _crossCorrelation(self, ts1, ts2):
		try:
			mean1 = sum(ts1) / len(ts1)
			mean2 = sum(ts2) / len(ts2)

			if len(ts1) != len(ts2):
				raise MyException("the length of two time series is not equal")
			
			numerator = 0
			for i in range(0, len(ts1)):
				numerator = numerator + (ts1[i]-mean1)*(ts2[i]-mean2)
			
			denominator_left = 0
			for i in range(0, len(ts1)):
				denominator_left = denominator_left + (ts1[i]-mean1)*(ts1[i]-mean1)
			denominator_left = math.sqrt(denominator_left)

			denominator_right = 0
			for i in range(0, len(ts2)):
				denominator_right = denominator_right + (ts2[i]-mean2)*(ts2[i]-mean2)
			denominator_right = math.sqrt(denominator_right)

			return numerator / (denominator_left*denominator_right)
		except Exception, exception:
			print "_crossCorrelation => ", exception


	def _processFeedbackFile(self, filename, feedback):
		del feedback[:]
		
		try:
			fhandler = open(filename, "r")
			dat = fhandler.readline()
			fhandler.close()

			dat = dat.split(",")

			beg_index=0
			while beg_index<len(dat):
				if dat[beg_index].split(":")[0] == "s":
					break
				beg_index=beg_index+1

			end_index=len(dat)-1
			while end_index>beg_index:
				if dat[end_index].split(":")[0] == "p":
					break
				end_index=end_index-1

			beg = long( dat[beg_index].split(":")[1] )
			end = long( dat[end_index].split(":")[1] )
		
			space = 0
			index = beg_index+1
			while index < end_index:
				if dat[index].split(":")[0] == "pp":
					if dat[index+1].split(":")[0] == "c":
						space = space + long(dat[index+1].split(":")[1]) - long(dat[index].split(":")[1])
						index = index + 2
					else:
						if index < end_index-1:
							print filename, " [pp,c] does not match"
						index = index + 1
				elif dat[index].split(":")[0] == "b":
					elapse = long(dat[index].split(":")[1]) - beg - space
					feedback.append(elapse)
					index = index + 1
				else:
					print filename, " ", dat[index], " => weird format"
					index = index+1
		
		except Exception, exception:
			print exception
		
		return (end-beg)

	
	def _getDataOfVideo(self, videoId, aggregated):
		del aggregated[:]

		cls = Batch

		try:
			ts_set = []
			coder_dat_buf = dict()
			videoL = 999999999

			for c in cls.coder_set:
				ts = []
				
				name = "+".join( [c, videoId] )
				if name in cls.outlier_buffer:
					continue
				
				filename = os.path.join(cls.data_root, "feedback/"+name+".txt")
				print "[_getDataOfVideo] reading => ", filename

				feedback = []
				videoLen = self._processFeedbackFile( filename, feedback )
				coder_dat_buf[name] = feedback

				if videoLen < videoL: 
					videoL = videoLen
			
			for k in coder_dat_buf.iterkeys():
				v = coder_dat_buf[k]
				if v[-1] - v[0] > videoL + 1500:
					cls.outlier_buffer[k] = 1
					print "[_getDataOfVideo] ", k, " is outlier"
				else:
					ts_set.append(v)

			aggregated = self._aggregate(ts_set, videoL)
			return videoL
		
		except Exception, exception:
			raise MyException("[_getDataOfVideo] raises exception" + str(exception))


	def process(self, videoId, coders):
		cls = Batch

		consensus = []
		videoL = self._getDataOfVideo( videoId, consensus )
		
		ts_set = []
		
		for coder in coders:
			name = "+".join( [coder, videoId] )
			if name in cls.outlier_buffer:
				continue

			filename = os.path.join(cls.data_root, "feedback/"+name+".txt")
			feedback = []
			videoLen = self._processFeedbackFile( filename, feedback )

			if videoLen > videoL + 1500:
				print "[process] ", filename, " is outlier"
				continue
			else:
				ts_set.append(feedback)

		combined = self._aggregate(ts_set, videoL)

		feedback_num = sum(combined)
		feedback_ent = self._entropy(combined)
		feedback_cor = self._crossCorrelation(consensus, combined)

		print feedback_num, "\t", feedback_ent, "\t", feedback_cor

		return [feedback_num, feedback_ent, feedback_cor]

	
	# user needs to decide the value of num 
	def observe(self, videoId, attr, num):
		try:
			cls = Batch

			view = []

			for coder in cls.coder_info_buffer.iterkeys():
				if attr == "gender" or attr == "loc":
					value = coder_info_buffer[coder][attr]
				elif attr == "psi":
					filename = os.path.join(cls.data_root, "psi/" + coder + "+" + videoId + ".txt")
					fhandler = open(filename)
					value = float(fhandler.readline())
					fhandler.close()
				else:
					value = float(coder_info_buffer[coder][attr])

				view.append( [coder, value] )

			view = sorted( view, key=lambda ele: ele[1] )

			json.dumps(view)

			coder_set1 = []
			coder_set2 = []
			
			for i in range(0, num):
				coder_set1.append( view[i][0] )
				coder_set2.append( view[-1-i][0] )
			
			stat1 = self.process(videoId, coder_set1)
			stat2 = self.process(videoId, coder_set2)

		except Exception, exception:
			print "observe => ", exception

	


if __name__ == "__main__":
	pass