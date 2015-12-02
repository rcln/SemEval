#!/usr/bin/env python
# -*- coding: utf-8
import argparse
import time
import os
from subprocess import Popen, PIPE, STDOUT
import random
from utils import load_all_phrases, load_all_gs
from collections import Counter

verbose = lambda *a: None 

if __name__ == "__main__":
    #Las opciones de línea de comando
    p = argparse.ArgumentParser('stats.py')
    p.add_argument("DIR",default=None,
            action="store", help="Directory with year to replicate")
    p.add_argument("OUTPUT",default=None,
            action="store", help="Directory for output")
    p.add_argument("--year",default=2015,
                action="store", dest="year",
                help="Year to evaluate")
    p.add_argument("--script-eval",default=[
        "perl",
        "english_testbed/data/2015/evaluate/correlation-noconfidence.pl"],
                action="store", dest="script",
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


    for (filename, phrases) in test_data:
        bits=filename.split('.')
        filename=bits[0]+'.output.'+bits[3]+'.txt'
        fn=open(os.path.join(opts.OUTPUT,filename),'w')
        for pair in phrases:
            num=random.random()
            print >> fn, "{0:1.1f}".format(num*5)
        filename_gs=os.path.join(opts.DIR,'test',bits[0]+'.'+str(opts.year)+'.gs.'+bits[3]+'.txt')
        filename_sys=os.path.join(opts.OUTPUT,filename)

        cmd=opts.script+[filename_gs,filename_sys]
        verbose(" ".join(cmd))
        p = Popen(cmd,  stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        print stdout



    

