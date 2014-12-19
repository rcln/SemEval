#!/usr/bin/python
import sys, random
from scipy.stats.stats import pearsonr

try :
	gs_file=sys.argv[1]
	ans_file=sys.argv[2]
except :
	print "usage: correlation.py gs_file ans_file"

#print gs_file, ans_file
gs_arr=[]
ans=[]
f1=open(gs_file, "r")

for l in f1.xreadlines():
	els=l.split()
	gs_arr.append(float(els[0]))
f1.close()

f2=open(ans_file, "r")

for l in f2.xreadlines():
	els=l.split()
	ans.append(float(els[0]))
f2.close()

#random test
#rda=[]
#for i in xrange(len(gs_arr)):
#	rda.append((random.random()*5))
	
if len(gs_arr)==len(ans):
	print "Pearson: ", pearsonr(gs_arr, ans)
else:
	print "Wrong size in results"