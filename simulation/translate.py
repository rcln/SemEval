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
import keys

verbose = lambda *a: None 


def translate(to_translate,outfile):
    #translations=service.translations().list(
    #    source=opts.source,
    #    target=opts.target,
    #    q=['carro', 'este es un carro']
    #                      ).execute())

    translations={'translations':[x[0] for x in to_translate]}
    for i,translation in enumerate(translations['translations']):
        outfile.write(u"{0}\t{1}\n".format(translation,to_translate[i][1]))


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
    p.add_argument("--target",default='en',
                action="store", dest="target",type=str,
                help="Target language")
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

    verbose('Conecting to google translate')
    service = build('translate', 'v2',
            developerKey=keys.GOGLE_TRANSLATE_DEV_API_KEY)

    train_data=[]
    verbose('Loading phrases in directory', opts.DIR)
    data=load_all_phrases(opts.DIR)
    verbose('Total train phrases',sum([len(d) for n,d in train_data]))
    for filename,phrases in data:
        verbose('Procesando', filename)
        to_translate=[]
        total_chars=0
        with codecs.open(os.path.join(opts.OUTPUT,filename+".translation"),"w",encoding='utf-8') as outfile:
            for phrase in phrases:
                if total_chars+len(phrase[0])>4000:
                    translate(to_translate,outfile)
                    to_translate=[]
                    total_chars=0
                print phrase[0]
                to_translate.append(phrase)
                total_chars+=len(phrase[0])
            translate(to_translate,outfile)




