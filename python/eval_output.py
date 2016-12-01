#!/usr/bin/env python
# -*- coding: utf-8
import argparse
import time
import os
import random
from utils import * 
from collections import Counter
from fill_samsung_owl import *

verbose = lambda *a: None 

if __name__ == "__main__":
    #Las opciones de línea de comando
    p = argparse.ArgumentParser('stats.py')
    p.add_argument("GSDIR",default=None,
            action="store", help="GS directory")
    p.add_argument("SYSDIR",default=None,
            action="store", help="SYS directory")
    p.add_argument("--distance",default='cosine', type=str,
                action="store", dest="distance",
                help="Distance to use")
    p.add_argument("--preprocessing",default='nltk-tokenise', type=str,
                action="store", dest="preprocessing",
                help="Preprocessing to do on the phrases")
    p.add_argument("--phrasevector",default='sum', type=str,
                action="store", dest="phrasevector",
                help="How to calculate phrasevector")
    p.add_argument("--diff",default=1.0, type=float,
                action="store", dest="diff",
                help="When verbose difference to use")
 
    p.add_argument("--no-stopwords",
                action="store_true", dest="nostop",default=False,
                help="Not to use stopwords [Off]")
    p.add_argument("--model",default='data/model.data', type=str,
                action="store", dest="model",
                help="Filename of the model to use (it is a python dictionary)")
    p.add_argument("--script-eval",default=[
        "perl",
        "english_testbed/data/2015/evaluate/correlation-noconfidence.pl"],
                action="store", dest="cmd",
                help="Verbose mode [Off]")
    p.add_argument("-v", "--verbose",
                action="store_true", dest="verbose",
                help="Verbose mode [Off]")
    p.add_argument("--filter",default='.',
                action="store", dest="filter_test",type=str,
                help="Regular expression to filter the test")
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
    p.add_argument("--standout_threshold", type=float,
                action="store", dest="standout_threshold",default=0.0,
                help="Threshold to stand out phrase pairs (positive = pairs with score difference > than; negative = score difference < than) [0.0]")
    p.add_argument("--logxphrase",
                action="store_true", dest="logxphrase",default=False,
                help="Produce Log for each phrase.. used for analyze outliers [Off]")    

    opts = p.parse_args()

    if opts.verbose:
        def verbose(*args):
            print " ".join([str(a) for a in args])
  
    filenames_sys=[os.path.join(opts.SYSDIR,filename) for filename 
            in os.listdir(opts.SYSDIR) if filename.endswith('.txt')]

    eval_all(opts.cmd,opts.GSDIR,filenames_sys,
            opts=opts)
   
