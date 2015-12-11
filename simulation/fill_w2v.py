#!/usr/bin/env python
# -*- coding: utf-8
import argparse
import time
import os
import random
from utils import * 
from collections import Counter
from scipy.spatial.distance import cosine
import requests
import json
import pickle
import nltk, re, pprint
from nltk import word_tokenize

verbose = lambda *a: None 


def distances_phrases_sum(phr1,phr2):
    acc1=np.zeros(300)
    nacc1=0
    acc2=np.zeros(300)
    nacc2=0
    for word in word_tokenize(phr1):
        try:
            acc1+=model[word]
            nacc1+=1
        except KeyError:
            pass
    for word in word_tokenize(phr2):
        try:
            acc2+=model[word]
            nacc2+=1
        except KeyError:
            pass
    if nacc1>0 and nacc2>0:
        dist= cosine(acc1/nacc1,acc2/nacc2)
        return np.nan_to_num(dist)
    else:
        return 0.0



if __name__ == "__main__":
    #Las opciones de línea de comando
    p = argparse.ArgumentParser('stats.py')
    p.add_argument("DIR",default=None,
            action="store", help="Directory with year to replicate")
    p.add_argument("OUTPUT",default=None,
            action="store", help="Directory for output")
    p.add_argument("--model",default='data/model.data', type=str,
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
    with open(opts.model,'rb') as idxf:
        model = pickle.load(idxf)

    train_data=[]
    verbose('Loading training')
    train_data=load_all_phrases(os.path.join(opts.DIR,'train'))
    verbose('Total train phrases',sum([len(d) for n,d in train_data]))
    train_gs = dict(load_all_gs(os.path.join(opts.DIR,'train')))
    verbose('Total train gs',sum([len(d) for n,d in train_gs.iteritems()]))

    verbose('Loading testing')
    test_data=load_all_phrases(os.path.join(opts.DIR,'test'))
    verbose('Total test phrases',sum([len(d) for n,d in test_data]))

    ## Compute for train data
    train_output={}
    for (filename, phrases) in train_data:
        filename_old=filename.replace('input', 'gs')
        train_output[filename_old]=[]
        for phr1,phr2 in phrases:
            num=distances_phrases_sum(phr1,phr2)
            train_output[filename_old].append(num)

    ## Train model    
    verbose('Training model')
    svr = train_model(train_gs, train_output,args={'kernel':'rbf'})


    filenames_sys=[]
    distances=[]
    for (filename, phrases) in test_data:
        bits=filename.split('.')
        filename=os.path.join(opts.OUTPUT,bits[0]+'.output.'+bits[3]+'.txt')
        fn=open(filename,'w')
        for phr1,phr2 in phrases:
            num=distances_phrases_sum(phr1,phr2)
            num=svr.predict(num)
            print >> fn, "{0:1.1f}".format(num[0])
        filenames_sys.append(filename)

    for corpus,res in eval_all(opts.cmd,os.path.join(opts.DIR,'test'),
                filenames_sys):
        print "{0:<40}: {1:<1.4f}".format(corpus,abs(res))
   

        

    

    

