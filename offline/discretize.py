#!/usr/bin/env python
from __future__ import division
import os
import math

# discretize user's personality measurement for ANOVA analysis
class Discretize:
	attribution = ["amazonId", "total", "match", "common", "mismatch", "location", "otherfocus", "gender", "age",
		"shyness", "extroversion", "neuroticism", "agreeableness", "conscientiousness", "openness", "selfconsciousness", "selfmonitor"]


	data = []


	def _load(self, filename):
		cls = Discretize

		del cls.data[:]

		fhandle = open(filename, "r")
		lines = fhandle.readlines()
		fhandle.close()

		for l in lines:
			tokens = l.strip().split("\t")
			cls.data.append(tokens)


	
	def _discretize(self, raw, output):
		del output[:]

		mean = sum(raw)/len(raw)

		std = 0
		for item in raw:
			std = std + (item-mean)*(item-mean)
		std = std / (len(raw)-1)
		std = math.sqrt(std)

		for item in raw:
			if item <= mean-std:
				output.append("low")
			elif item >= mean+std:
				output.append("high")
			else:
				output.append("mid")


	def discretize(self, attr):
		cls = Discretize

		if not cls.data: return None

		attrIndex = -1
		try:
			attrIndex = cls.attribution.index(attr)
		except ValueError:
			raise Exception("invalid attribution name")

		size = len(cls.data)
		values = []
		for i in range(0, size):
			print "[", i, "]"
			values.append( float(cls.data[i][attrIndex]) )

		symbols = []
		self._discretize(values, symbols)

		print attr, attrIndex, len(symbols)

		return symbols

	
	def normalizeTarget(self):
		cls = Discretize

		if not cls.data: return None

		size = len(cls.data)
		targets = []
		for i in range(0, size):
			total = float(cls.data[i][1])
			match = float(cls.data[i][2])
			targets.append( match/total )

		return targets


	def process(self, filename):
		cls = Discretize

		base = os.path.basename(filename)
		videoId = os.path.splitext(base)[0]

		print videoId

		self._load(filename)

		shyness = self.discretize("shyness")
		openness = self.discretize("openness")
		otherfocus = self.discretize("otherfocus")
		neuroticism = self.discretize("neuroticism")
		selfmonitor = self.discretize("selfmonitor")
		extroversion = self.discretize("extroversion")
		agreeableness = self.discretize("agreeableness")
		conscientiousness = self.discretize("conscientiousness")
		selfconsciousness = self.discretize("selfconsciousness")

		targets = self.normalizeTarget()
		print "targets", len(targets)

		size = len(cls.data)
		fhandle = open("discretize/"+videoId+".txt", "w")
		for i in range(0, size):
			line = [
				str(targets[i]),
				videoId,
				cls.data[i][5],
				cls.data[i][7],
			#	str(cls.data[i][8]),
				shyness[i],
				openness[i],
				otherfocus[i],
				neuroticism[i],
				selfmonitor[i],
				extroversion[i],
				agreeableness[i],
				conscientiousness[i],
				selfconsciousness[i]
			]

			line = "\t".join(line)
			line = line + "\n"
			fhandle.write(line)
		fhandle.close()


if __name__ == "__main__":
	app = Discretize()
	
	app.process("personality/4M8tfXK8Y1Y.txt")
	
	app.process("personality/l_S-RM-8l9w.txt")
	
	app.process("personality/UcaYbyw8MZo.txt")
	
	app.process("personality/qrHqKOkHNME.txt")
	
	app.process("personality/f7e91xGHQJ8.txt")
	
	app.process("personality/f_U76yiaexg.txt")
	
	app.process("personality/xAZ3-QGMWjo.txt")
	
	app.process("personality/bfBMc4RDafg.txt")







