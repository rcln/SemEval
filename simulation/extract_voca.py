#!/usr/bin/env python
# -*- coding: utf-8
import argparse
import time
import os
import random
from utils import * 
from collections import Counter
from gensim.models.word2vec import Word2Vec
from scipy.spatial.distance import cosine
import requests
import json
import nltk, re, pprint
from nltk import word_tokenize
import pickle 

verbose = lambda *a: None 


if __name__ == "__main__":
    #Las opciones de línea de comando
    p = argparse.ArgumentParser('stats.py')
    p.add_argument("DIR",default=None,
            action="store", help="Directory with year to replicate")
    p.add_argument("OUTPUT",default=None,
            action="store", help="Directory for output")
    p.add_argument("-l",default=False,
                action="store_true", dest="use_local_model",
                help="Flag to use the local model")
    p.add_argument("--server",default="http://turing.iimas.unam.mx:5001", type=str,
                action="store", dest="server",
                help="Server address")
    p.add_argument("--model",default='data/GoogleNews-vectors-negative300.bin', type=str,
                action="store", dest="model",
                help="Word2vec model to use")
    p.add_argument("--year",default='2015', type=str,
                action="store", dest="year",
                help="Year to evaluate")
    p.add_argument("--script-eval",default=[
        "perl",
        "english_testbed/data/2015/evaluate/correlation-noconfidence.pl"],
                action="store", dest="cmd",
                help="Verbose mode [Off]")
    p.add_argument("-v", "--verbose",
                action="store_true", dest="verbose",
                help="Verbose mode [Off]")
    opts = p.parse_args()

    if opts.verbose:
        def verbose(*args):
            print " ".join([str(a) for a in args])

    verbose("Loading model",opts.model)
    model = Word2Vec.load_word2vec_format(opts.model, binary=True)

    train_data=[]
    verbose('Starting training')
    train_data=load_all_phrases(os.path.join(opts.DIR,'train'))
    verbose('Total train phrases',sum([len(d) for n,d in train_data]))
    train_gs = dict(load_all_gs(os.path.join(opts.DIR,'train')))
    verbose('Total train gs',sum([len(d) for n,d in train_gs.iteritems()]))

    ## Compute for train data
    train_output={}
    DATA={}
    for (filename, phrases) in train_data:
        filename_old=filename.replace('input', 'gs')
        train_output[filename_old]=[]
        for phr1,phr2 in phrases:
            words= word_tokenize(phr1)
            for word in words:
                if DATA.has_key(word):
                    continue
                else:
                    try:
        if opts.use_local_model:
                        DATA[word]=model[word]
                    except KeyError:
                        DATA[word]=np.zeros(300)
            words= word_tokenize(phr2)
            for word in words:
                if DATA.has_key(word):
                    continue
                else:
                    try:
                        DATA[word]=model[word]
                    except KeyError:
                        DATA[word]=np.zeros(300)
                                        


    verbose('Starting testing')
    test_data=load_all_phrases(os.path.join(opts.DIR,'test'))
    verbose('Total test phrases',sum([len(d) for n,d in test_data]))

   
    for (filename, phrases) in test_data:
        filename_old=filename.replace('input', 'gs')
        train_output[filename_old]=[]
        for phr1,phr2 in phrases:
            words= word_tokenize(phr1)
            for word in words:
                if DATA.has_key(word):
                    continue
                else:
                    try:
                        DATA[word]=model[word]
                    except KeyError:
                        DATA[word]=np.zeros(300)
            words= word_tokenize(phr2)
            for word in words:
                if DATA.has_key(word):
                    continue
                else:
                    try:
                        DATA[word]=model[word]
                    except KeyError:
                        DATA[word]=np.zeros(300)
 
    
    with open("model.data",'wb') as idxf:
            pickle.dump(DATA, idxf, pickle.HIGHEST_PROTOCOL)
