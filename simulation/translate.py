#!/usr/bin/env python
# -*- coding: utf-8
import argparse
import time
import os
import random
from utils import * 
from collections import Counter
from googleapiclient.discovery import build
import keys

verbose = lambda *a: None 

if __name__ == "__main__":
    #Las opciones de línea de comando
    p = argparse.ArgumentParser('stats.py')
    p.add_argument("DIR",default=None,
            action="store", help="Directory with year to replicate")
    p.add_argument("OUTPUT",default=None,
            action="store", help="Directory for output")
    p.add_argument("--filter",default='.',
                action="store", dest="filter_test",type=str,
                help="Regular expression to filter the test")
    p.add_argument("-v", "--verbose",
                action="store_true", dest="verbose",
                help="Verbose mode [Off]")
 
    opts = p.parse_args()

    if opts.verbose:
        def verbose(*args):
            print " ".join([str(a) for a in args])


    train_data=[]
    verbose('Loading phrases in directory', opts.DIR)
    data=load_all_phrases(opts.DIR)
    verbose('Total train phrases',sum([len(d) for n,d in train_data]))
    for filename,phrases in data:
        for phrase in phrases:
            print phrase[0]


    verbose('Conecting to google translate')
    service = build('translate', 'v2',developerKey='')
