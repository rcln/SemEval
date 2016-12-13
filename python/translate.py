#!/usr/bin/env python
# -*- coding: utf-8
import argparse
import time
import os
import random
import codecs
from utils import * 
from collections import Counter
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import keys
import time

verbose = lambda *a: None 

# -*- coding: utf-8 -*-
#
from nltk.corpus import stopwords   # stopwords to detect language
from nltk import wordpunct_tokenize # function to split up our words
from sys import stdin               # how else should we get our input :)
 
def get_language_likelihood(input_text):
    """Return a dictionary of languages and their likelihood of being the 
    natural language of the input text
    """
 
    input_text = input_text.lower()
    input_words = wordpunct_tokenize(input_text)
 
    language_likelihood = {}
    total_matches = 0
    for language in stopwords._fileids:
        language_likelihood[language] = len(set(input_words) &
                set(stopwords.words(language)))
 
    return language_likelihood
 
def get_language(input_text):
    """Return the most likely language of the given text
    """
 
    likelihoods = get_language_likelihood(input_text)
    return sorted(likelihoods, key=likelihoods.get, reverse=True)[0]
 


def translate(to_translate,outfile,first=False):
    if first:
        translations=service.translations().list(
            source=opts.source,
            target=opts.target,
            q=[x[0] for x in to_translate]
                              ).execute()
        for i,translation in enumerate(translations[u'translations']):
            outfile.write(u"{0}\t{1}\n".format(translation[u'translatedText'],to_translate[i][1]))
    else:
        sntcs=[]
        for pair in to_translate:
            sntcs.append(pair[0])
            sntcs.append(pair[1])
        translations=service.translations().list(
                source=opts.source,
                target=opts.target,
                q=sntcs).execute()
        translations=translations[u'translations']
        for i in range(len(translations)/2):
            outfile.write(u"{0}\t{1}\n".format(translations[2*i]['translatedText'],translations[2*i+1]['translatedText']))

if __name__ == "__main__":
    #Las opciones de línea de comando
    p = argparse.ArgumentParser('stats.py')
    p.add_argument("DIR",default=None,
            action="store", help="Directory with year to replicate")
    p.add_argument("OUTPUT",default=None,
            action="store", help="Directory for output")
    p.add_argument("--source",default='es',
                action="store", dest="source",type=str,
                help="Source language")
    p.add_argument("--crosslingual",default=False,
                action="store_true", dest="crosslingual",
                help="Croslingual corpus (only translate on)")
    p.add_argument("--target",default='en',
                action="store", dest="target",type=str,
                help="Target language")
    p.add_argument("--fortmat",default=None,
                action="store", dest="format",type=str,
                help="Format (None for most, 2017 for new crosslingual)")
    p.add_argument("-v", "--verbose",
                action="store_true", dest="verbose",
                help="Verbose mode [Off]")
    opts = p.parse_args()

    if opts.verbose:
        def verbose(*args):
            print " ".join([str(a) for a in args])

    verbose('Conecting to google translate')
    service = build('translate', 'v2',
            developerKey=keys.GOGLE_TRANSLATE_DEV_API_KEY)

    train_data=[]
    verbose('Loading phrases in directory', opts.DIR)
    data=load_all_phrases(opts.DIR,format=opts.format)
    verbose('Total train phrases',sum([len(d) for n,d in train_data]))
    for filename,phrases in data:
        verbose('Procesando', filename)
        to_translate=[]
        total_chars=0
        if os.path.exists(os.path.join(opts.OUTPUT,filename[:-4]+".translation.txt")):
            continue
        with codecs.open(os.path.join(opts.OUTPUT,filename[:-4]+".translation.txt"),"w",encoding='utf-8') as outfile:
            for phrase in phrases:
                if opts.crosslingual:
                    if total_chars+len(phrase[0])>3000:
                        translate(to_translate,outfile,first=True)
                        to_translate=[]
                        total_chars=0
                    l1=get_language(phrase[0])
                    l2=get_language(phrase[1])
                    if l1=="english":
                          to_translate.append((phrase[1],phrase[0]))
                    else:
                        to_translate.append(phrase)
                    total_chars+=len(phrase[0])
                else:
                    if total_chars+len(phrase[0])+len(phrase[1])>3000:
                        translate(to_translate,outfile)
                        to_translate=[]
                        total_chars=0
                    to_translate.append(phrase)
                    total_chars+=len(phrase[0])+len(phrase[1])
            translate(to_translate,outfile,first=opts.crosslingual)
