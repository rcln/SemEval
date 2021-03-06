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
from array import *

# [OWL 20160202]
import string
from nltk.corpus import stopwords
stopwds = stopwords.words('english')
punctuation = set(string.punctuation)
punctuation.add('´´')
punctuation.add('``')
punctuation.add('\'\'')

from scipy.stats import spearmanr
import copy


verbose = lambda *a: None 
verbose2 = lambda *a: None 

global_aligns=[]
min_threshold_correlation=0.25

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
def align(model,phr1,phr2,opts={}):
    if opts.align_method=="localmax":
        align=align_localmax(model,phr1,phr2,opts)
        if opts.logxphrase:
            global_aligns.append(align)
        return align
    else:
        sys.exit("Error: invalid alignment method")

def sts(model,phr1,phr2,key,aligns_model,opts={}):    
    scores=[]

    
    verbose2(' '.join(phr1) +  "\n" + ' '.join(phr2) + "\n" + ("-"*10))
    
    if aligns_model:
        partial = sts_external_alignment(phr1,phr2,key,aligns_model,model,opts)
        scores.extend(partial)

        verbose2("Align_EXT-->" + str(partial))
    if opts.sts_method=="bidirectional":
        partial = sts_bidirectional(model,phr1,phr2,opts)
        scores.extend( partial )

        verbose2("Align_BID-->" + str(partial) )
    elif opts.sts_method=="simple":
        partial = sts_simple(model,phr1,phr2,opts)
        scores.extend( partial )

        verbose2("Align_SIM-->" + str(partial))
    elif opts.sts_method=="none":
        verbose2("NO local alignment")
    else:
        sys.exit("Error: invalid STS method")

    verbose2("\n\n")
        
    return scores

def sts_external_alignment(phr1,phr2,key,aligns_model,w2v_model,opts={}):        

    # print key
    try:
        lr,rl = aligns_model[key]
    except:
        verbose(str(key) + "-->NO ALIGNMENT FOUND")
        return [0.00,0.00,0.00]
    
    opts_ = copy.copy(opts)
    opts_.align_threshold=0.06

    alignments = [lr,rl]
    # LEFT-RIGTH [LR] alignment
    score=0
    scores=array('f')
    num_alignments=0
    idx_alignment=-1
    for alignment in alignments:

    
        idx_alignment+=1
        alignment_score=0
        alignment_score_wn=0
        num_wn_scores=0
        aligns2check=[]
        if alignment:
            # [OWL 20160202] discard punctuation alignment
            alignment[1] = [x for x in alignment[1] if x[0] not in punctuation and x[1] not in punctuation]

            #[OWL 20160202] complement alignmet
            if opts.complement_ext_alignment:
                if(idx_alignment==0):
                    comp_alignment=complement_external_alignment(phr1, phr2, alignment[1], w2v_model, opts_)
                else:
                    comp_alignment=complement_external_alignment(phr2, phr1, alignment[1], w2v_model, opts_)
                if comp_alignment:
                    alignment[1].extend([[x[0],x[1]] for x in comp_alignment])
                    alignment[0].extend([x[3] for x in comp_alignment])


            if alignment[1] and len(alignment[1])>0:
                num_alignments+=1                
                for pair in alignment[1]:
                    sim = score_alignment(pair, w2v_model, opts)
                    # verbose2(str(pair) +"-->" + str(sim))
                    alignment_score += sim
                    aligns2check.append([pair[0], pair[1], sim])
                    if opts.wn_distance:
                        wn_sim = score_alignment_wn(pair,opts)
                        if wn_sim:
                            num_wn_scores+=1                            
                            alignment_score_wn += wn_sim

                if opts.wn_check:
                    penalties=sum(check_in_wordnet([aligns2check])[0])
                    alignment_score-=penalties

                # alignment_score=alignment_score/len(alignment[1]) # normalize
                # [OWL 20160202]                
                alignment_score=alignment_score/(len(phr1) if len(phr1)>len(phr2) else len(phr2)) # normalize

                # [OWL 20160202] penalize shifts in alignment order
                if opts.penalize_shift_ext:
                    sorted_alignment=sorted(alignment[0], key=lambda v:v[0])
                    corr=spearmanr(sorted_alignment)[0]
                    if corr>min_threshold_correlation: # if too small it is not used
                        alignment_score= alignment_score*(corr)
                #---
                scores.append(alignment_score)

                if opts.wn_distance:
                    if num_wn_scores==0:
                        num_wn_scores=1
                    alignment_score_wn=alignment_score_wn/num_wn_scores # normalize
                    scores.append(alignment_score_wn)
            else:
                verbose2(str(key) + "-->EMPTY ALIGNMENT [" + str(idx_alignment)+"]")
                scores.append(0.00)
                if opts.wn_distance:
                    scores.append(0.00)
        else:            
            verbose(str(key) + "-->NO ALIGNMENT[" + str(idx_alignment)+"]")
            scores.append(0.00)
            if opts.wn_distance:
                scores.append(0.00)            

        score+=alignment_score

    # if num_alignments==0:
    #     num_alignments=1
    # score = score/num_alignments # se divide entre numero de alineamientos que contribyeron
    # scores.append(alignment_score)


    # verbose2("Align_Ext-" + str(key) + "==>" + str(scores))
    return scores


# [OWL 20160202] try to fill in the gaps in external alignment (unaligned words)
def complement_external_alignment(phr1, phr2, alignment, w2v_model, opts={}):
    aligned_1=[]
    aligned_2=[]
    for pair in alignment:
        aligned_1.append(pair[0])
        aligned_2.append(pair[1])

    unaligned_1=[x for x in phr1 if x not in aligned_1]
    unaligned_2=[x for x in phr2 if x not in aligned_2]

    complement = align(w2v_model, unaligned_1, unaligned_2, opts)
    return complement

def score_alignment(aligned_pair, w2v_model, opts={}):
    score=0    
    w1=aligned_pair[0]
    w2=aligned_pair[1]    

    sim=similarity(w2v_model,[w1.lower()],[w2.lower()],opts) # cosine distance for word2vec
    score+=sim
    return score

def score_alignment_wn(aligned_pair, opts={}):
    w1=aligned_pair[0]
    w2=aligned_pair[1]
    w1_syn=wn.synsets(w1, pos=wn.NOUN)
    w2_syn=wn.synsets(w2, pos=wn.NOUN)    
    if w1_syn and w2_syn:        
        sim = w1_syn[0].path_similarity(w2_syn[0], simulate_root=True)        
    else:
        return None

    if not sim:
        return None

    return sim

def sts_simple(model,phr1,phr2,opts={}):
    aligns = align(model,phr1,phr2,opts)
    
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

def sts_bidirectional(model,phr1,phr2,opts={}):
    # align dir 1
    aligns = align(model,phr1,phr2,opts)    
    score1 = 0.0;
    for w1,w2,dist,pairs in aligns:
        score1=score1+dist
        # print "w2vA-->" + repr(w1) + "--" + repr(w2) + "==" + str(dist)
    if aligns:
        if(opts.ooc_penalty > 0): # Out of Context penalization
            ooc = len(phr1)-len(aligns)
            score1 = score1 - abs(ooc * opts.ooc_penalty)
        score1 = score1 / (2*len(aligns))
    
        # [OWL 20160202] penalize shifts in alignment order
        if opts.penalize_shift_local:
            sorted_alignment=sorted([x[3] for x in aligns], key=lambda v:v[0])
            corr=spearmanr(sorted_alignment)[0]
            if corr>min_threshold_correlation: # if too small it is not used
                score1= score1*(corr)
        #---    

    # align dir 2
    aligns2 = align(model,phr2,phr1, opts)    
    score2 = 0.0;
    for w1,w2,dist,pairs in aligns2:
        score2=score2+dist        
        # print "w2vB-->" + repr(w1) + "--" + repr(w2) + "==" + str(dist)
    if aligns2: 
        # print "S2->" + str(score2)
        if(opts.ooc_penalty > 0): # Out of Context penalization
            ooc = len(phr2)-len(aligns2)
            score2 = score2 - abs(ooc * opts.ooc_penalty)
        score2 = score2 / (2*len(aligns2))

        # [OWL 20160202] penalize shifts in alignment order
        if opts.penalize_shift_local:
            sorted_alignment=sorted([x[3] for x in aligns2], key=lambda v:v[0])
            corr=spearmanr(sorted_alignment)[0]
            if corr>min_threshold_correlation: # if too small it is not used
                score2= score2*(corr)
        #---            

    penalties=check_in_wordnet([aligns, aligns2])    
    total_penalty1=sum(penalties[0])
    total_penalty2=sum(penalties[1])
    # for pen in penalties:
    #     total_penalty+=sum(pen)


    # print "total_penalty=" + str(total_penalty)

    # print "STS-->" + str(score1+score2)
    # print [score1,score2,score1+score2, -total_penalty]
    # return [score1,score2,score1+score2, -total_penalty]
    res = [(score1-total_penalty1),(score2-total_penalty2),((score1+score2)-(total_penalty1+total_penalty2))]

    # no negative components
    for x in xrange(0,len(res)-1):
        if res[x]<0.0:
            res[x]=0.0

    # sep=" "
    # verbose2("Align_Bi-" + sep.join(phr1) +  "-" + sep.join(phr2) + "==>" + str(res))
    return res


# align words using local maximum (i.e. for each word1 get max similarity in words2)
def align_localmax(model,phr1,phr2,opts):
    words1 = phr1;
    words2 = phr2;
    words2_ = [w for w in words2]
    w2_idxs = [x for x in xrange(0,(len(words2)))]

    w1_idx=-1    
    aligns = []    
    for word1 in words1:
        w1_idx+=1
        distances=[]
        try:
            model[word1]
        except:
            continue
        for word2 in words2_:
            try:
                model[word2]
            except:
                distances.append(0.0) # preserve indexes 
                continue
            num=similarity(model,[word1],[word2],opts) # cosine distance for word2vec
            distances.append(np.nan_to_num(num))            
            #print "{0} {1}: {2}".format(repr(word1),repr(word2),num)

        if distances: # not empty            
            idx=np.argmax(distances)

            isaligned=False
            if opts.align_threshold > 0: # align threshold (out of context words OOC => len(phr1) - len(aligns))
                if distances[idx] > opts.align_threshold:
                    isaligned=True
            else: # no align threshold (every word is aligned)
                isaligned=True


            if(isaligned):
                aligns.append([word1, words2_[idx], float("{0:.4f}".format(distances[idx])), [w1_idx, w2_idxs[idx]] ])
                # remove aligned target word
                words2_.pop(idx)  
                w2_idxs.pop(idx)
    #print "Phrase 1:", phr1
    #print "Phrase 2:", phr2
    #print "Aligns  :", aligns
    return aligns

def remove_punctuation(text):
    return ''.join(x for x in text if x not in punct)        


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
    p.add_argument("--filter_train",default='.',
                action="store", dest="filter_train",type=str,
                help="Regular expression to filter the train")
    p.add_argument("--filter_test",default='.',
                action="store", dest="filter_test",type=str,
                help="Regular expression to filter the test")
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

    #data/align.data
    p.add_argument("--alignments-model",default='', type=str,
                action="store", dest="aligns_model_path",
                help="Filename of alignments to use (it is a python dictionary)")
    p.add_argument("--include-wn-distance",
                action="store_true", dest="wn_distance",default=False,
                help="True = include WordNet distance for alignments")     
    p.add_argument("--check-in-wordnet",
                action="store_true", dest="wn_check",default=False,
                help="Check aligns in wordnet, penalize antonyms and DSCs (default False)") 



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
    # [OWL 20160202]
    p.add_argument("--penalize-shift-ext",default=False,
                action="store_true", dest="penalize_shift_ext",
                help="Penalize shifted order in external alignment by Spearman rank order correlation (default False) ")    
    p.add_argument("--penalize-shift-local",default=False,
                action="store_true", dest="penalize_shift_local",
                help="Penalize shifted order in local alignment by Spearman rank order correlation (default False) ")        
    p.add_argument("--complement-ext-alingment",default=False,
                action="store_true", dest="complement_ext_alignment",
                help="Align unaligned word in external alignment with w2vec (default False) ")            

    p.add_argument("--logxphrase",
                action="store_true", dest="logxphrase",default=False,
                help="Produce Log for each phrase.. used for analyze outliers [Off]")    

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
    train_data=load_all_phrases(os.path.join(opts.DIR,'train'),filter=opts.filter_train)
    verbose('Total train phrases',sum([len(d) for n,d in train_data]))
    train_gs = dict(load_all_gs(os.path.join(opts.DIR,'train')))
    verbose('Total train gs',sum([len(d) for n,d in train_gs.iteritems()]))

    # [Pseudo: 2] Se cargan datos de prueba
    verbose('Loading testing')
    test_data=load_all_phrases(os.path.join(opts.DIR,'test'),filter=opts.filter_test)
    verbose('Total test phrases',sum([len(d) for n,d in test_data]))

    # [Pseudo: 3 ] Se cargan vectores por palabras
    verbose("Loading model",opts.model)
    with open(opts.model,'rb') as idxf:
        model = pickle.load(idxf)

    # se carga alineaciones externas
    aligns_model=None
    if opts.aligns_model_path:
        verbose("Loading external alignments",opts.aligns_model_path)
        with open(opts.aligns_model_path,'rb') as idxf:
            aligns_model = pickle.load(idxf)

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
        phrIdx=-1
        for phr1,phr2 in phrases:
            phrIdx+=1        
            counter=counter+1
            print_progress(counter, count_phrases)
            # [Pseudo: 4.a.i ] Preprocesamiento
            key=(filename,phrIdx)
            phr1,phr2=preprocessing(phr1,phr2,opts)
            # [Pseudo: 4.a.ii ] Sumar vectores frase uno
            # [Pseudo: 4.a.iii ] Sumar vectores frase dos
            # [Pseudo: 4.a.iv ] Calcular distancia
            if opts.logxphrase:
                global_aligns=[]

            num=sts(model,phr1,phr2,key,aligns_model, opts)
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
        filename_old=filename
        count_phrases = len(phrases)
        counter=0
        bits=filename.split('.')
        filename=os.path.join(opts.OUTPUT,bits[0]+'.output.'+bits[3]+'.txt')
        fn=open(filename,'w')
        if opts.logxphrase:
            flog=open(filename[:-3]+"log", "w")
        # [Pseudo:66.a ] Por cada frase de corpos de prueba
        phrIdx=-1
        for phr1,phr2 in phrases:
            phrIdx+=1
            counter=counter+1
            print_progress(counter, count_phrases)
            # [Pseudo: 6.a.i ] Preprocesamiento
            h,t=os.path.split(filename_old)
            key=(t,phrIdx)
            phr1,phr2=preprocessing(phr1,phr2,opts)
            # [Pseudo: 6.a.ii ] Sumar vectores frase uno
            # [Pseudo: 6.a.iii ] Sumar vectores frase dos
            # [Pseudo: 6.a.iv ] Calcular distancia
            if opts.logxphrase:
                global_aligns=[]
            num_raw=sts(model,phr1,phr2,key,aligns_model,opts)
            # Se mapea resultado de distancia a score semeval 
            # num_raw_reshaped=np.reshape(num_raw, -1, len(num_raw))
            num=method.predict([num_raw])
            print >> fn, "{0:1.1f}".format(num[0])
            if opts.logxphrase:
                print >> flog, "{0:1.1f}|{1}|{2}|{3}|{4}".format(num[0], num_raw, phr1, phr2, global_aligns)
        filenames_sys.append(filename)

    
    # [Pseudo: 7 ] Evaluar
    eval_all(opts.cmd,os.path.join(opts.DIR,'test'),
                filenames_sys,opts=opts)
   
    # eval_all_local(opts.cmd,os.path.join(opts.DIR,'test'), filenames_sys,0.0)

        

    

    

