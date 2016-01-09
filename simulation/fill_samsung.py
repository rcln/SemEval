#!/usr/bin/env python
# -*- coding: utf-8

# SE IMPORTAN LAS LIBRERIAS
import argparse
import time
import os
import random
from utils import * 
from collections import Counter
from distances_semeval import *
from fill_w2v import *
from scipy.spatial.distance import cosine
import requests
import json
import pickle
import re
from aligments import *
verbose = lambda *a: None 


if __name__ == "__main__":
    #Las opciones de línea de comando
    p = argparse.ArgumentParser('stats.py')
    p.add_argument("DIR",default=None,
            action="store", help="Directory with year to replicate")
    p.add_argument("OUTPUT",default=None,
            action="store", help="Directory for output")
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
    p.add_argument("--model",default='data/model.data', type=str,
                action="store", dest="model",
                help="Filename of the model to use (it is a python dictionary)")
    p.add_argument("--year",default='2015', type=str,
                action="store", dest="year",
                help="Year to evaluate")
    p.add_argument("--no-stopwords",
                action="store_true", dest="nostop",default=False,
                help="Not to use stopwords [Off]")
    p.add_argument("--script-eval",default=[
        "perl",
        "english_testbed/data/2015/evaluate/correlation-noconfidence.pl"],
                action="store", dest="cmd",
                help="Verbose mode [Off]")
    p.add_argument("-v", "--verbose",
                action="store_true", dest="verbose",
                help="Verbose mode [Off]")
    p.add_argument("-vv", "--verbose-extra",
                action="store_true", dest="verbose2",
                help="Verbose mode [Off]")
    opts = p.parse_args()

    if opts.verbose:
        def verbose(*args):
            print " ".join([str(a) for a in args])

    if opts.verbose2:
        def verbose2(*args):
            print " ".join([str(a) for a in args])

    # [Pseudo: 1] Se cargan datos de entrenamiento 
    train_data=[]
    verbose('Loading training')
    train_data=load_all_phrases(os.path.join(opts.DIR,'train'))
    verbose('Total train phrases',sum([len(d) for n,d in train_data]))
    train_gs = dict(load_all_gs(os.path.join(opts.DIR,'train')))
    verbose('Total train gs',sum([len(d) for n,d in train_gs.iteritems()]))

    # [Pseudo: 2] Se cargan datos de prueba
    verbose('Loading testing')
    test_data=load_all_phrases(os.path.join(opts.DIR,'test'))
    verbose('Total test phrases',sum([len(d) for n,d in test_data]))

    # [Pseudo: 3 ] Se cargan vectores por palabras
    verbose("Loading model",opts.model)
    with open(opts.model,'rb') as idxf:
        model = pickle.load(idxf)

    ## Se itera sobre corpus, frases
    train_output={}

    # [Pseudo: 4 ] Por cada corpus de entrenamiento 
    for (filename, phrases) in train_data:
        filename_old=filename.replace('input', 'gs')
        train_output[filename_old]=[]
        # [Pseudo: 4.a ] Por cada frase de corpos de entrenamiento
        for phr1,phr2 in phrases:
            # [Pseudo: 4.a.i ] Preprocesamiento
            phr1,phr2=preprocessing(phr1,phr2,opts)
            # [Pseudo: 4.a.ii ] Sumar vectores frase uno
            # [Pseudo: 4.a.iii ] Sumar vectores frase dos
            # [Pseudo: 4.a.iv ] Calcular distancia
            alignment=word_alignment(model,phr1,phr2,opts)
            verbose2(alignment)
            phr1=[w for w,w2,d in alignment if w2]
            phr2=[w2 for w,w2,d in alignment if w2]
            num=distance(model,phr1,phr2,opts)
            train_output[filename_old].append(num)

    # [Pseudo: 5 ] Entrenar regresor
    verbose('Training model')
    if opts.method=="svr":
        method = train_model_srv(train_gs, train_output,args={'kernel':'rbf'})
    ## PARA AGREGAR UN MÉTODO MÁS
    # if opts.method == "nombre":
    #   method =  train_model_nombre(train_gs, train_output,args={'kernel':'rbf'})
    #   train_model_nombre tienen que estar en utils


    filenames_sys=[]
    distances=[]
    # [Pseudo: 6 ] Por cada corpus de prueba
    for (filename, phrases) in test_data:
        bits=filename.split('.')
        filename=os.path.join(opts.OUTPUT,bits[0]+'.output.'+bits[3]+'.txt')
        fn=open(filename,'w')
        # [Pseudo:66.a ] Por cada frase de corpos de prueba
        for phr1,phr2 in phrases:
            # [Pseudo: 6.a.i ] Preprocesamiento
            phr1,phr2=preprocessing(phr1,phr2,opts)
            # [Pseudo: 6.a.ii ] Sumar vectores frase uno
            # [Pseudo: 6.a.iii ] Sumar vectores frase dos
            # [Pseudo: 6.a.iv ] Calcular distancia
            alignment=word_alignment(model,phr1,phr2,opts)
            verbose2(alignment)
            phr1=[w for w,w2,d in alignment if w2]
            phr2=[w2 for w,w2,d in alignment if w2]
            num=distance(model,phr1,phr2,opts)
            # Se mapea resultado de distancia a score semeval 
            num=method.predict(num)
            print >> fn, "{0:1.1f}".format(num[0])
        filenames_sys.append(filename)

    
    # [Pseudo: 7 ] Evaluar
    for corpus,res in eval_all(opts.cmd,os.path.join(opts.DIR,'test'),
                filenames_sys):
        print "{0:<40}: {1:<1.4f}".format(corpus,abs(res))
   

        

    

    

