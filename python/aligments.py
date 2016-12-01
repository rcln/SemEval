#!/usr/bin/env python
# -*- coding: utf-8
import numpy as np
from distances_semeval import *
from fill_w2v import *

def word_alignment(model,phr1, phr2,opts={},thres=0.4):
    alignment=[]
    for n1,word1 in enumerate(phr1):
        distances=[]
        try:
            model[word1]
        except:
            alignment.append((n1,None,1.0))
            continue
        for word2 in phr2:
            try:
                model[word2]
            except:
                distances.append(1.0)
                continue
            distances.append(distance(model,[word1],[word2],opts))
        idx=np.argmin(distances)
        d=np.min(distances)
        if d<thres:
            alignment.append((n1,idx,d))     
        else:
            alignment.append((n1,None,1.0))     
    return alignment2words(alignment,phr1,phr2)

def alignment2words(alignment,phr1,phr2):
    alignment_=[]
    for n1,n2,d in alignment:
        if n2:
            alignment_.append((phr1[n1],phr2[n2],d))
        else:
            alignment_.append((phr1[n1],None,d))
    return alignment_
