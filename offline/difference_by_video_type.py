#!/usr/bin/env python
from __future__ import division
import os
import math
import json
from batch import Batch

class DifferenceByVideoType:
	
	batch = None

	def init(self):
		cls = DifferenceByVideoType

		cls.batch = Batch()
		cls.batch.load("/Users/lixinghu/Documents/projects/ThesisProject/analysis/data/")

	
	# condition is a dict to be used to filter coder
	def _filter(self, coder, conditions):
		for k in conditions.iterkeys():
			v = conditions[k]
			if coder[k] != v:
				return False
		return True


	def observe(self, videoId, conditions):
		cls = DifferenceByVideoType

		try:
			filtered_coder = []
			for coder in cls.batch.coder_info_buffer.iterkeys():
				if not self._filter(cls.batch.coder_info_buffer[coder], conditions):
					continue
				filtered_coder.append(coder)

			stat = cls.batch.process(videoId, filtered_coder)
			return stat
		except Exception, exception:
			print "_process => ", exception
		
	
if __name__ == "__main__":
	app = DifferenceByVideoType()

	app.init()

	video_info = {
		"4M8tfXK8Y1Y": ["f", 186, 5.75],
		"bfBMc4RDafg": ["m", 129, 4],
		"f_U76yiaexg": ["m", 113, 5.25],
		"f7e91xGHQJ8": ["f", 183, 5],
		"l_S-RM-8l9w": ["m", 106, 4.25],
		"qrHqKOkHNME": ["f", 130, 6.75],
		"UcaYbyw8MZo": ["m", 219, 2.75],
		"xAZ3-QGMWjo": ["f", 127, 5.38]
	}

	for k in video_info:
		empty_conditions = {}
		stat = app.observe( k, empty_conditions )
		video_len = video_info[k][1]
		average_feedback_num = stat[0] / video_len
		print k, " => ", average_feedback_num, stat[1], stat[2]


		