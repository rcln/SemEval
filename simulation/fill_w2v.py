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

verbose = lambda *a: None 

if __name__ == "__main__":
    #Las opciones de línea de comando
    p = argparse.ArgumentParser('stats.py')
    p.add_argument("DIR",default=None,
            action="store", help="Directory with year to replicate")
    p.add_argument("OUTPUT",default=None,
            action="store", help="Directory for output")
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


    train_data=[]
    verbose('Starting training')
    train_data=load_all_phrases(os.path.join(opts.DIR,'train'))
    verbose('Total train phrases',sum([len(d) for n,d in train_data]))

    verbose('Starting testing')
    test_data=load_all_phrases(os.path.join(opts.DIR,'test'))
    verbose('Total test phrases',sum([len(d) for n,d in test_data]))

    print opts.model
    model = Word2Vec.load_word2vec_format(opts.model, binary=True)


    filenames_sys=[]
    distances=[]
    for (filename, phrases) in test_data:
        bits=filename.split('.')
        filename=os.path.join(opts.OUTPUT,bits[0]+'.output.'+bits[3]+'.txt')
        fn=open(filename,'w')
        for phr1,phr2 in phrases:
            acc1=np.zeros(300)
            nacc1=0
            acc2=np.zeros(300)
            nacc2=0
            for word in phr1.split():
                try:
                    acc1+=model[word]
                    nacc1+=1
                except KeyError:
                    pass
            for word in phr2.split():
                try:
                    acc2+=model[word]
                    nacc2+=1
                except KeyError:
                    pass
            if nacc1>0 and nacc2>0:
                dist=cosine(acc1/nacc1,acc2/nacc2)
                distances.append(dist)
            else:
                distances.append(0.0)
            print dist
            print >> fn, "{0:1.1f}".format(dist*5)
                    

    print "Maxima distancia", max(distances)
    for corpus,res in eval_all(opts.cmd,os.path.join(opts.DIR,'test'),
                filenames_sys):
        print "{0:<40}: {1:<1.4f}".format(corpus,abs(res))
   

        

    

    

