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

unig={}
big={}
trig={}

for file in corfiles:
	f=codecs.open("refcorp/"+lang+"/"+file, "r", encoding="utf-8")
	for line in f.readlines():
		sentences = sentence_splitter.tokenize(line.strip())
		for sen in sentences:
			words_rough=PunktWordTokenizer().tokenize(sen)
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
	
f_out=codecs.open("unifreq_"+lang+".dat", "w", encoding="utf-8")
for k in unig.keys():
	f_out.write(k+"\t"+str(unig[k])+"\n")
f_out.close()

f_out=codecs.open("bifreq_"+lang+".dat", "w", encoding="utf-8")
for k in big.keys():
	f_out.write(k[0]+" "+k[1]+"\t"+str(big[k])+"\n")
f_out.close()

f_out=codecs.open("trifreq_"+lang+".dat", "w", encoding="utf-8")
for k in trig.keys():
	f_out.write(k[0]+" "+k[1]+" "+k[2]+"\t"+str(trig[k])+"\n")
f_out.close()