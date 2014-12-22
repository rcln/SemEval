#!/usr/bin/python
import sys, codecs
import nltk
import nltk.data
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.util import bigrams
from nltk.util import trigrams

import pickle
import math

from os import listdir


def compare_histogram(hist1, hist2):
	#weighted dice
	k1=set(hist1.keys())
	k2=set(hist2.keys())
	
	sv1=float(sum(hist1.values()))
	sv2=float(sum(hist2.values()))
	
	ks=k1 & k2
	somma=0
	for k in ks:
		p1=float(hist1[k])/sv1
		p2=float(hist2[k])/sv2
		
		p=math.sqrt(p1*p2)
		somma+=p
	
	return somma
	#return 2*float(somma)/float(len(hist1)+len(hist2))
"""

def compare_histogram(hist1, hist2):
	#dice
	k1=set(hist1.keys())
	k2=set(hist2.keys())
	
	ks=k1 & k2
	return 2*float(len(ks))/float(len(hist1)+len(hist2))
"""
try:
	input_file=sys.argv[1]
	lang=sys.argv[2]
except:
	print "usage: "+sys.argv[0]+" <input_datafile> <lang>"
	sys.exit(-1)

models={} #maps model_name into model

for file in listdir("models/"+lang):
	f=open("models/"+lang+"/"+file, "r")
	mdl=pickle.load(f)
	models[file]=mdl
	f.close()

if lang=="en":
	sentence_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
else:
	sentence_splitter = nltk.data.load('tokenizers/punkt/spanish.pickle')
	
unig={}
big={}
trig={}

sumslen=0
nsen=0
	
f=codecs.open(input_file, "r", encoding="utf-8")
for line in f.readlines():
	sentences = sentence_splitter.tokenize(line.strip())
	for sen in sentences:
		words_rough=PunktWordTokenizer().tokenize(sen)
		sumslen+=len(words_rough)
		nsen+=1
		words=[]
		for wo in words_rough:
			w=wo.strip('.')
			words.append(w)
		for wo in words:
			try:
				cw=unig[w]
			except:
				cw=0
			cw+=1
			unig[w]=cw
			
		bg=bigrams(words)
		for b in bg:
			try:
				cb=big[b]
			except:
				cb=0
			cb+=1
			big[b]=cb
			
		tg=trigrams(words)
		for t in tg:
			try:
				ct=trig[t]
			except:
				ct=0
			ct+=1
			trig[t]=ct
f.close()

msim=[]
slens={}

for k in models.keys():
	m=models[k]
	uv=compare_histogram(m["unigrams"], unig)
	bv=compare_histogram(m["bigrams"], big)
	tv=compare_histogram(m["trigrams"], trig)
	maslen=m["aslen"]
	aslen=float(sumslen)/float(nsen)
	lc=math.sqrt(math.pow(maslen-aslen, 2))
	lv=float(1)-lc/float(max((maslen, aslen)))
	avg_sim=(uv+2*bv+3*tv)/float(6)
	
	msim.append((k, avg_sim))
	slens[k]=lv
	
msim.sort(key=lambda x: -x[1])

for el in msim:
	print "mdl: "+el[0]+" s: %4f" % el[1], "l: %4f" % slens[el[0]]