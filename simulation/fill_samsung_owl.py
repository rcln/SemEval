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
import numpy as np
import sys
from nltk.corpus import wordnet

verbose = lambda *a: None 
verbose2 = lambda *a: None 


#def preprocessing(phr1,phr2):
#    if opts.preprocessing=="nltk-tokenise":
#        phr1=preprocessing_nltk_tokenise(phr1)
#        phr2=preprocessing_nltk_tokenise(phr2)
#    # PARA AGREGAR UNA OPCION DE PREPROCESADO MÁS SEGUIR
#    # if opts.preprocessing=="nombre":
#    #   phr1=nombre_funcion_en_utils(phr1)
#    #   phr2=nombre_funcion_en_utils(phr2)
#    
#    return phr1,phr2


#def distance(model,phr1,phr2):
#    # primero se calcula los vectores
#    if opts.phrasevector=="none":
#        pass
#    if opts.phrasevector=="sum":
#        # [Pseudo: 4.a.ii ] Sumar vectores frase uno
#        vec1=vector_sum(model,phr1)
#        # [Pseudo: 4.a.iii ] Sumar vectores frase dos
#        vec2=vector_sum(model,phr2)
#    # PARA AGREGAR UNA OPCION DE CALCULO DE VECTOR MÁS SEGUIR
#    # if opts.phrasevector=="nombre":
#    #   VEC1=nombre_funcion_en_utils(phr1)
#    #   VEC2=nombre_funcion_en_utils(phr2)
#    
#
#    # Segundo se calcula la medida de distancia
#    # [Pseudo: 4.a.iv ] Calcular distancia
#    if opts.distance=="cosine":
#        num=1-distances_cosine(vec1,vec2)
#    # PARA AGREGAR UNA DISTANCIA MÁS SEGUIR
#    # if opts.distance=="nombre"
#    #   num=nombre_funcion_en_distances_semeval(model,phr1,phr2)
#
#    num=np.nan_to_num(num)
#    return num
#
def align(model,phr1,phr2):
    if opts.align_method=="localmax":
        return align_localmax(model,phr1,phr2)
    else:
        sys.exit("Error: invalid alignment method")

def sts(model,phr1,phr2):
    if opts.sts_method=="bidirectional":
        return sts_bidirectional(model,phr1,phr2)
    if opts.sts_method=="simple":
        return sts_simple(model,phr1,phr2)
    else:
        sys.exit("Error: invalid STS method")

def sts_simple(model,phr1,phr2):
    aligns = align(model,phr1,phr2)
    
    # Loop aligns and compute distance
    score = 0;
    for w1,w2,dist in aligns:
        score=score+dist

    if aligns:
        if(opts.ooc_penalty > 0): # Out of Context penalization
            ooc = len(phr1)-len(aligns)
            score = score - (ooc * opts.ooc_penalty)
        score = score / len(aligns)

    return score

def sts_bidirectional(model,phr1,phr2):
    # align dir 1
    aligns = align(model,phr1,phr2)    
    score1 = 0;
    for w1,w2,dist in aligns:
        score1=score1+dist    
    if aligns: 
        # print "S1->" + str(score1)
        if(opts.ooc_penalty > 0): # Out of Context penalization
            ooc = len(phr1)-len(aligns)
            score1 = score1 - (ooc * opts.ooc_penalty)
        score1 = score1 / 2*len(aligns)

    # align dir 2
    aligns = align(model,phr2,phr1)    
    score2 = 0;
    for w1,w2,dist in aligns:
        score2=score2+dist    
    if aligns: 
        # print "S2->" + str(score2)
        if(opts.ooc_penalty > 0): # Out of Context penalization
            ooc = len(phr2)-len(aligns)
            score2 = score2 - (ooc * opts.ooc_penalty)
        score2 = score2 / 2*len(aligns)

    # print "STS-->" + str(score1+score2)
    return score1+score2

# align words using local maximum (i.e. for each word1 get max similarity in words2)
def align_localmax(model,phr1,phr2):
    words1 = phr1;
    words2 = phr2;

    aligns = []
    for word1 in words1:
        distances=[]
        try:
            model[word1]
        except:
            continue
        for word2 in words2:
            try:
                model[word2]
            except:
                distances.append(0.0) # preserve indexes 
                continue
            num=similarity(model,[word1],[word2],opts) # cosine distance for word2vec
            distances.append(np.nan_to_num(num))
            # print "{0} {1}: {2}".format(repr(word1),repr(word2),num)

        if distances: # not empty            
            idx=np.argmax(distances)

            isaligned=False
            if opts.align_threshold > 0: # align threshold (out of context words OOC => len(phr1) - len(aligns))
                if distances[idx] > opts.align_threshold:
                    isaligned=True
            else: # no align threshold (every word is aligned)
                isaligned=True


            if(isaligned):
                aligns.append([word1, words2[idx], distances[idx]])
                # remove aligned target word
                words2.pop(idx)    

    return aligns

def print_progress(counter, count_phrases):
    sys.stdout.write("[%d / %d]   \r" % (counter, count_phrases) )
    sys.stdout.flush()

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
    p.add_argument("--no-stopwords",
                action="store_true", dest="nostop",default=False,
                help="Not to use stopwords [Off]")
    p.add_argument("-v", "--verbose",
                action="store_true", dest="verbose",
                help="Verbose mode [Off]")
    p.add_argument("-vv", "--verbose-extra",
                action="store_true", dest="verbose2",
                help="Verbose mode [Off]")

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
        print ""
        print "Training -- " + filename        
        count_phrases = len(phrases)
        counter=0
        filename_old=filename.replace('input', 'gs')
        train_output[filename_old]=[]
        # [Pseudo: 4.a ] Por cada frase de corpos de entrenamiento
        for phr1,phr2 in phrases:
            counter=counter+1
            print_progress(counter, count_phrases)
            # [Pseudo: 4.a.i ] Preprocesamiento
            phr1,phr2=preprocessing(phr1,phr2,opts)
            # [Pseudo: 4.a.ii ] Sumar vectores frase uno
            # [Pseudo: 4.a.iii ] Sumar vectores frase dos
            # [Pseudo: 4.a.iv ] Calcular distancia
            num=sts(model,phr1,phr2)
            train_output[filename_old].append(num)
            # max_sentences = max_sentences - 1
            # if max_sentences<=0:
                # sys.exit("PRUEBAS")

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
    counter=0
    for (filename, phrases) in test_data:
        print ""
        print "Test -- " + filename
        count_phrases = len(phrases)
        counter=0
        bits=filename.split('.')
        filename=os.path.join(opts.OUTPUT,bits[0]+'.output.'+bits[3]+'.txt')
        fn=open(filename,'w')
        # [Pseudo:66.a ] Por cada frase de corpos de prueba
        for phr1,phr2 in phrases:
            counter=counter+1
            print_progress(counter, count_phrases)
            # [Pseudo: 6.a.i ] Preprocesamiento
            phr1,phr2=preprocessing(phr1,phr2,opts)
            # [Pseudo: 6.a.ii ] Sumar vectores frase uno
            # [Pseudo: 6.a.iii ] Sumar vectores frase dos
            # [Pseudo: 6.a.iv ] Calcular distancia
            num=sts(model,phr1,phr2)
            # Se mapea resultado de distancia a score semeval 
            num=method.predict(num)
            print >> fn, "{0:1.1f}".format(num[0])
        filenames_sys.append(filename)

    
    # [Pseudo: 7 ] Evaluar
    for corpus,res in eval_all(opts.cmd,os.path.join(opts.DIR,'test'),
                filenames_sys):
        print "{0:<40}: {1:<1.4f}".format(corpus,abs(res))
   

        

    

    

