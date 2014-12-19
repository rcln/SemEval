#!/usr/bin/python
import random, sys

nlines = int(sys.argv[1])

for i in xrange(nlines):
	#val = random.uniform(4, 5)
	val = random.normalvariate(2.5, 2.5)
	if val < 0: val = 0.0
	if val > 5: val = 5.0
	print val


