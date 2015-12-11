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
from scipy.spatial.distance import cosine
import requests
import json
import pickle
verbose = lambda *a: None 


def preprocessing(phr1,phr2):
    if opts.preprocessing=="nltk-tokenise":
        phr1=preprocessing_nltk_tokenise(phr1)
        phr2=preprocessing_nltk_tokenise(phr2)
    # PARA AGREGAR UNA OPCION DE PREPROCESADO MÁS SEGUIR
    # if opts.preprocessing=="nombre":
    #   phr1=nombre_funcion_en_utils(phr1)
    #   phr2=nombre_funcion_en_utils(phr2)
    
    return phr1,phr2


def distance(model,phr1,phr2):
    # primero se calcula los vectores
    if opts.phrasevector=="none":
        pass
    if opts.phrasevector=="sum":
        vec1=vector_sum(model,phr1)
        vec2=vector_sum(model,phr2)
    # PARA AGREGAR UNA OPCION DE CALCULO DE VECTOR MÁS SEGUIR
    # if opts.phrasevector=="nombre":
    #   VEC1=nombre_funcion_en_utils(phr1)
    #   VEC2=nombre_funcion_en_utils(phr2)
    

    # Segundo se calcula la medida de distancia
    if opts.distance=="cosine":
        num=distances_cosine(vec1,vec2)
        num=np.nan_to_num(num)
    # PARA AGREGAR UNA DISTANCIA MÁS SEGUIR
    # if opts.distance=="nombre"
    #   num=nombre_funcion_en_distances_semeval(model,phr1,phr2)

    return num




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

    # Se carga el modelo
    verbose("Loading model",opts.model)
    with open(opts.model,'rb') as idxf:
        model = pickle.load(idxf)

    # Se cargan datos de prueba
    train_data=[]
    verbose('Loading training')
    train_data=load_all_phrases(os.path.join(opts.DIR,'train'))
    verbose('Total train phrases',sum([len(d) for n,d in train_data]))
    train_gs = dict(load_all_gs(os.path.join(opts.DIR,'train')))
    verbose('Total train gs',sum([len(d) for n,d in train_gs.iteritems()]))

    # Se cargan datos de evaluación
    verbose('Loading testing')
    test_data=load_all_phrases(os.path.join(opts.DIR,'test'))
    verbose('Total test phrases',sum([len(d) for n,d in test_data]))

    ## Se itera sobre corpus, frases
    train_output={}
    for (filename, phrases) in train_data:
        filename_old=filename.replace('input', 'gs')
        train_output[filename_old]=[]
        for phr1,phr2 in phrases:
            phr1,phr2=preprocessing(phr1,phr2)
            num=distance(model,phr1,phr2)
            train_output[filename_old].append(num)

    ## Se entrena modelo
    verbose('Training model')
    if opts.method=="svr":
        method = train_model_srv(train_gs, train_output,args={'kernel':'rbf'})
    ## PARA AGREGAR UN MÉTODO MÁS
    # if opts.method == "nombre":
    #   method =  train_model_nombre(train_gs, train_output,args={'kernel':'rbf'})
    #   train_model_nombre tienen que estar en utils


    filenames_sys=[]
    distances=[]
    for (filename, phrases) in test_data:
        bits=filename.split('.')
        filename=os.path.join(opts.OUTPUT,bits[0]+'.output.'+bits[3]+'.txt')
        fn=open(filename,'w')
        for phr1,phr2 in phrases:
            phr1,phr2=preprocessing(phr1,phr2)
            num=distance(model,phr1,phr2)
            # Se mapea resultado de distancia a score semeval 
            num=method.predict(num)
            print >> fn, "{0:1.1f}".format(num[0])
        filenames_sys.append(filename)

    for corpus,res in eval_all(opts.cmd,os.path.join(opts.DIR,'test'),
                filenames_sys):
        print "{0:<40}: {1:<1.4f}".format(corpus,abs(res))
   

        

    

    

