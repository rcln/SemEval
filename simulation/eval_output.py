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
    p.add_argument("GSDIR",default=None,
            action="store", help="GS directory")
    p.add_argument("SYSDIR",default=None,
            action="store", help="SYS directory")
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

    
    filenames_sys=[os.path.join(opts.SYSDIR,filename) for filename 
            in os.listdir(opts.SYSDIR) if filename.endswith('.txt')]

    total=[]
    for corpus,res in  eval_all(opts.cmd,opts.GSDIR,filenames_sys):
        print "{0:<40}: {1:<1.4f}".format(corpus,abs(res))

        

    

    
