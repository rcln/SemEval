#!/usr/bin/env python
# -*- coding: utf-8
import argparse
import time
import os
import random
from utils import * 
from collections import Counter

verbose = lambda *a: None 

if __name__ == "__main__":
    #Las opciones de línea de comando
    p = argparse.ArgumentParser('stats.py')
    p.add_argument("DIR",default=None,
            action="store", help="Directory with year to replicate")
    p.add_argument("OUTPUT",default=None,
            action="store", help="Directory for output")
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
    train_gs = dict(load_all_gs(os.path.join(opts.DIR,'train')))
    print train_gs.keys()
    verbose('Total train phrases',sum([len(d) for n,d in train_data]))

    ## Compute for train data
    train_output={}
    for (filename, phrases) in train_data:
        print "1-->"+filename
        filename_old=filename.replace('input', 'gs')
        train_output[filename_old]=[]
        bits=filename.split('.')

        for pair in phrases:
            num=random.random()
            train_output[filename_old].append(num)


    ## Train model    
    svr = train_model(train_gs, train_output)


    verbose('Starting testing')
    test_data=load_all_phrases(os.path.join(opts.DIR,'test'))
    verbose('Total test phrases',sum([len(d) for n,d in test_data]))


    filenames_sys=[]
    for (filename, phrases) in test_data:
        bits=filename.split('.')
        filename=os.path.join(opts.OUTPUT,bits[0]+'.output.'+bits[3]+'.txt')
        fn=open(filename,'w')
        for pair in phrases:
            num=random.random()
            print "Antes %f"%num
            num = svr.predict(num)
            print "Despues %f"%num

            #### STARS Code to label phrases
            print >> fn, "{0:1.1f}".format(num[0])
            #### ENDS code to label phrases

        filenames_sys.append(filename)




    for corpus,res in eval_all(opts.cmd,os.path.join(opts.DIR,'test'),
                filenames_sys):
        print "{0:<40}: {1:<1.4f}".format(corpus,abs(res))
   
        

    

    

