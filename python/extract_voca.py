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
import pickle 
from fill_w2v import preprocessing

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
    p.add_argument("--method",default='svr', type=str,
                action="store", dest="method",
                help="Method to use during trainning")
    p.add_argument("--distance",default='cosine', type=str,
                action="store", dest="distance",
                help="Distance to use")
    p.add_argument("--phrasevector",default='sum', type=str,
                action="store", dest="phrasevector",
                help="How to calculate phrasevector")
    p.add_argument("--preprocessing",default='nltk-tokenise', type=str,
                action="store", dest="preprocessing",
                help="Preprocessing to do on the phrases")
    p.add_argument("--year",default='2015', type=str,
                action="store", dest="year",
                help="Year to evaluate")
    p.add_argument("--filter_train",default='.',
                action="store", dest="filter_train",type=str,
                help="Regular expression to filter the train")
    p.add_argument("--filter_test",default='.',
                action="store", dest="filter_test",type=str,
                help="Regular expression to filter the test")
    p.add_argument("--script-eval",default=[
        "perl",
        "english_testbed/data/2015/evaluate/correlation-noconfidence.pl"],
                action="store", dest="cmd",
                help="Verbose mode [Off]")
    p.add_argument("--no-stopwords",
                action="store_true", dest="nostop",default=False,
                help="Not to use stopwords [Off]")
    p.add_argument("-v", "--verbose",
                action="store_true", dest="verbose",
                help="Verbose mode [Off]")
    p.add_argument("-vv", "--verbose-extra",
                action="store_true", dest="verbose2",
                help="Verbose mode [Off]")

    # ALIGNMENT ------
    p.add_argument("--stsmethod",default='bidirectional', type=str,
                action="store", dest="sts_method",
                help="Semantic Textual Similarity method, default bidirectional")
    p.add_argument("--alignmethod",default='localmax', type=str,
                action="store", dest="align_method",
                help="Align method, default localmax")    
    p.add_argument("--alignthreshold",default=0.2, type=float,
                action="store", dest="align_threshold",
                help="Align threshold, default 0.2")
    p.add_argument("--oocpenalty",default=1.0, type=float,
                action="store", dest="ooc_penalty",
                help="Out of Context penalization, default 1.0")

    p.add_argument("--logxphrase",
                action="store_true", dest="logxphrase",default=False,
                help="Produce Log for each phrase.. used for analyze outliers [Off]")    


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
            phr1=codecs.encode(phr1,'utf-8','ignore')
            phr2=codecs.encode(phr2,'utf-8','ignore')
            phr1=''.join([i if ord(i) < 128 else ' ' for i in phr1])
            phr2=''.join([i if ord(i) < 128 else ' ' for i in phr2])
            words1,words2= preprocessing(phr1,phr2,opts)
            for word in words1:
                if DATA.has_key(word):
                    continue
                else:
                    try:
                        DATA[word]=model[word]
                    except KeyError:
                        DATA[word]=np.zeros(300)+0.025
            for word in words2:
                if DATA.has_key(word):
                    continue
                else:
                    try:
                        DATA[word]=model[word]
                    except KeyError:
                        DATA[word]=np.zeros(300)+0.025
                                        


    verbose('Starting testing')
    test_data=load_all_phrases(os.path.join(opts.DIR,'test'))
    verbose('Total test phrases',sum([len(d) for n,d in test_data]))

   
    for (filename, phrases) in test_data:
        filename_old=filename.replace('input', 'gs')
        train_output[filename_old]=[]
        for phr1,phr2 in phrases:
            phr1=codecs.encode(phr1,'utf-8','ignore')
            phr2=codecs.encode(phr2,'utf-8','ignore')
            phr1=''.join([i if ord(i) < 128 else ' ' for i in phr1])
            phr2=''.join([i if ord(i) < 128 else ' ' for i in phr2])
            words1,words2= preprocessing(phr1,phr2,opts)
            for word in words1:
                if DATA.has_key(word):
                    continue
                else:
                    try:
                        DATA[word]=model[word]
                    except KeyError:
                        DATA[word]=np.zeros(300)+0.025
            for word in words2:
                if DATA.has_key(word):
                    continue
                else:
                    try:
                        DATA[word]=model[word]
                    except KeyError:
                        DATA[word]=np.zeros(300)+0.025
 
    
    with open("model.data",'wb') as idxf:
            pickle.dump(DATA, idxf, pickle.HIGHEST_PROTOCOL)
