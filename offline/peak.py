#!/usr/bin/env python
from __future__ import division
from batch import Batch
import os
import math
import json
	

class Peak:
	
	batch = None

	
	def load(self, root):
		cls = Peak
		cls.batch = Batch()
		cls.batch.load(root)


	def _peakify(self, ts, res):
		del res[:]

		status = -1

		STAT_DOWN       = 0
		STAT_UP         = 1
		STAT_UPPLATO    = 2
		STAT_DOWNPLATO  = 3
		
		plato_beg = 0
		plato_end = 0
		
		for i in range(1, len(ts)):
			
			if ts[i] > ts[i-1]:
				status = STAT_UP
			
			elif ts[i] < ts[i-1]:
				if status == STAT_UP:
					res.append( [i-1, ts[i-1]] )
				elif status == STAT_UPPLATO:
					res.append( [round((plato_beg+plato_end)/2), ts[i-1]] )
				status = STAT_DOWN

			else:
				if status == STAT_UP:
					status = STAT_UPPLATO
					plato_beg = i-1
					plato_end = i
				elif status == STAT_DOWN:
					status = STAT_DOWNPLATO
					plato_beg = i-1
					plato_end = i
				else:
					plato_end = i
	
	
	def _filter(self, peaks, filtered_peaks, threshold):
		del filtered_peaks[:]
		for p in peaks:
			if p[1] >= threshold:
				filtered_peaks.append( p )

	
	def _combine_close(self, peaks):
		combined_peaks = []
		combined_peaks.append( peaks[0] )
		
		for i in range(1, len(peaks)):
			if peaks[i][0]-combined_peaks[-1][0] < 10:
				continue
			else:
				combined_peaks.append( peaks[i] )

		del peaks[:]
		for p in combined_peaks:
			peaks.append(p)



	def _display_peaks(self, peaks, num):
		for p in peaks:
			print p[0]/10, "\t", p[1]/num


	def _process(self, aggregated, num):
		# aggregated: the aggregated time series data of multiple coders
		# num: the number of coders
		peaks = []
		self._peakify(aggregated, peaks)

		filtered_peaks = []
		self._filter(peaks, filtered_peaks, num/5)
		self._combine_close(filtered_peaks)
		return filtered_peaks


	def get_tail_coders(self, videoId, attr, num):
		cls = Peak
		
		view = []

		for coder in cls.batch.coder_info_buffer.iterkeys():
			if coder not in cls.batch.coder_set:
				continue
			if attr == "gender" or attr == "loc":
				value = cls.batch.coder_info_buffer[coder][attr]
			elif attr == "psi":
				filename = os.path.join(cls.batch.data_root, "psi/" + coder + "+" + videoId + ".txt")
				fhandler = open(filename, "r")
				value = float(fhandler.readline())
				fhandler.close()
			else:
				value = float(cls.batch.coder_info_buffer[coder][attr])
			view.append( [coder, value] )
		
		view = sorted( view, key=lambda ele: ele[1] )

		coder_set1 = []
		coder_set2 = []
		if num > len(view)/2:
			raise Exception("too many coders")
		for i in range(0, num):
			coder_set1.append( view[i][0] )
			coder_set2.append( view[-1-i][0] )
		
		return [coder_set1, coder_set2]


	
	def aggregated_coders(self, videoId, coders):
		cls = Peak

		consensus = []
		videoL = cls.batch._getDataOfVideo( videoId, consensus )
		
		ts_set = []
		
		for coder in coders:
			if coder in cls.batch.outlier_buffer:
				continue

			name = "+".join( [coder, videoId] )
			
			feedback = []
			filename = os.path.join(cls.batch.data_root, "feedback/"+name+".txt")
			videoLen = cls.batch._processFeedbackFile( filename, feedback )

			ts_set.append(feedback)

		
		combined = cls.batch._aggregate(ts_set, videoL)

		return combined


	def peakify_coders(self, videoId, attr, num):
		coders = self.get_tail_coders(videoId, attr, num)
		combined1 = self.aggregated_coders(videoId, coders[0])
		combined2 = self.aggregated_coders(videoId, coders[1])

		peaks1 = self._process(combined1, len(coders[0]))
		peaks2 = self._process(combined2, len(coders[1]))

		return [peaks1, peaks2]


	
	def discretize(self, videoId, num):
		print "{", videoId, "}"

		aggregated = []

		cls = Peak
		cls.batch._getDataOfVideo(videoId, aggregated)

		peaks = self._process(aggregated, num)
		print "\nconsensus data"
		self._display_peaks(peaks, num)

		# configurable
		attribution = "agreeableness"
		tail_number = 56

		coder_peaks = self.peakify_coders(videoId, attribution, tail_number)
		print "\nlow", attribution
		self._display_peaks(coder_peaks[0], tail_number)
		print "\nhigh", attribution
		self._display_peaks(coder_peaks[1], tail_number)

		return peaks


if __name__ == "__main__":
	app = Peak()
	app.load("/Users/lixinghu/Documents/projects/ThesisProject/analysis/data/")
	app.discretize("qrHqKOkHNME", 350)




