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
from nltk.corpus import stopwords
from scipy.spatial.distance import *
stop = stopwords.words('english')
verbose = lambda *a: None 
verbose2 = lambda *a: None 
re_words=re.compile(r'\W')

def preprocessing(phr1,phr2,opts={}):
    verbose2('Preprocessing...')
    verbose2('Phrase 1:',phr1)
    verbose2('Phrase 2:',phr2)
    if opts.preprocessing=="nltk-tokenise":
        phr1=preprocessing_nltk_tokenise(phr1)
        phr2=preprocessing_nltk_tokenise(phr2)
    if opts.preprocessing=="nltk-tokenise-filter":
        phr1=preprocessing_nltk_tokenise(phr1)
        phr1=[w for w in phr1 if not re_words.match(w)
                                and len(w)>0]
        phr2=preprocessing_nltk_tokenise(phr2)
        phr2=[w for w in phr2 if not re_words.match(w)
                                and len(w)>0]
    if opts.preprocessing=="re":
        phr1=re_words.split(phr1.lower())
        phr1=[w for w in phr1 if len(w)>0]
        phr2=re_words.split(phr2.lower())
        phr2=[w for w in phr2 if len(w)>0]
    # PARA AGREGAR UNA OPCION DE PREPROCESADO MÁS SEGUIR
    # if opts.preprocessing=="nombre":
    #   phr1=nombre_funcion_en_utils(phr1)
    #   phr2=nombre_funcion_en_utils(phr2)
    if not opts.nostop:
        phr1=[w for w in phr1 if not w in stop]
        phr2=[w for w in phr2 if not w in stop]
    verbose2('Tokens phrase 1:',phr1)
    verbose2('Tokens phrase 2:',phr2)
    return phr1,phr2


def distance(model,phr1,phr2,opts={}):
    # primero se calcula los vectores
    if opts.phrasevector=="none":
        pass
    if opts.phrasevector=="sum":
        # [Pseudo: 4.a.ii ] Sumar vectores frase uno
        vec1=vector_sum(model,phr1)
        # [Pseudo: 4.a.iii ] Sumar vectores frase dos
        vec2=vector_sum(model,phr2)
    # PARA AGREGAR UNA OPCION DE CALCULO DE VECTOR MÁS SEGUIR
    # if opts.phrasevector=="nombre":
    #   VEC1=nombre_funcion_en_utils(phr1)
    #   VEC2=nombre_funcion_en_utils(phr2)
    

    # Segundo se calcula la medida de distancia
    # [Pseudo: 4.a.iv ] Calcular distancia
    # Default cosine
    num=cosine(vec1,vec2)
    if opts.distance=="correlation":
        num=correlation(vec1,vec2)
    if opts.distance=="euclidean":
        num=euclidean(vec1,vec2)
    if opts.distance=="seuclidean":
        num=euclidean(vec1,vec2)
 
    # PARA AGREGAR UNA DISTANCIA MÁS SEGUIR
    # if opts.distance=="nombre"
    #   num=nombre_funcion_en_distances_semeval(model,phr1,phr2)

    num=np.nan_to_num(num)
    return num


def similarity(model,phr1,phr2,opts={}):
    return 1-distance(model,phr1,phr2,opts)


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
    p.add_argument("--no-stopwords",
                action="store_true", dest="nostop",default=False,
                help="Not to use stopwords [Off]")
    p.add_argument("--year",default='2015', type=str,
                action="store", dest="year",
                help="Year to evaluate")
    p.add_argument("--script-eval",default=[
        "perl",
        "english_testbed/data/2015/evaluate/correlation-noconfidence.pl"],
                action="store", dest="cmd",
                help="Verbose mode [Off]")
    p.add_argument("--no-stop-words",
                action="store_true", dest="nostop",default=False,
                help="Not to use stopwords [Off]")
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
            num=distance(model,phr1,phr2,opts)
            # Se mapea resultado de distancia a score semeval 
            num=method.predict(num)
            print >> fn, "{0:1.1f}".format(num[0])
        filenames_sys.append(filename)

    
    # [Pseudo: 7 ] Evaluar
    for corpus,res in eval_all(opts.cmd,os.path.join(opts.DIR,'test'),
                filenames_sys):
        print "{0:<40}: {1:<1.4f}".format(corpus,abs(res))
   

        

    

    

