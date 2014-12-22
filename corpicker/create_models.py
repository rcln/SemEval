#!/usr/bin/python
import sys, codecs
import nltk
import nltk.data
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.util import bigrams
from nltk.util import trigrams

import pickle

from os import listdir

try:
	lang= sys.argv[1]
except:
	print "usage: "+sys.argv[0]+" <lang> (either 'en' or 'es')"
	sys.exit(-1)

if lang=="en":
	sentence_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
else:
	sentence_splitter = nltk.data.load('tokenizers/punkt/spanish.pickle')

corfiles=[]
for f in listdir("refcorp/"+lang):
	corfiles.append(f)

for file in corfiles:
	model={}
	unig={}
	big={}
	trig={}
	
	sumslen=0
	nsen=0
	
	f=codecs.open("refcorp/"+lang+"/"+file, "r", encoding="utf-8")
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
	
	model["unigrams"]=unig
	model["bigrams"]=big
	model["trigrams"]=trig
	model["aslen"]=float(sumslen)/float(nsen)
	
	f_out=open("models/"+lang+"/"+file+".mdl", "w")
	pickle.dump(model, f_out)
	f_out.close()
	