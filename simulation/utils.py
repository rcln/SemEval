#!/usr/bin/env python
# -*- coding: utf-8
import os
import re
import tempfile
from subprocess import Popen, PIPE, STDOUT
import numpy as np
from sklearn.svm import SVR
import codecs
import nltk, re, pprint
from nltk import word_tokenize


re_file=re.compile('.*\.input\..*\.txt$')
re_gs=re.compile('.*\.gs\..*\.txt$')

def load_phrases_from_file(dirname,filename):
    phrases=[]
    if not re_file.match(filename):
        return []

    with codecs.open(os.path.join(dirname,filename),encoding='utf-8') as data:
        for line in data:
            bits=line.strip().split('\t')
            if len(bits)==2:
                phrases.append((bits[0],bits[1]))
    return phrases

def load_gs_from_file(dirname,filename):
    gs=[]
    if not re_gs.match(filename):
        return []

    with open(os.path.join(dirname,filename)) as data:
        for line in data:
            line=line.strip()
            try:
                gs.append(float(line))
            except ValueError:
                gs.append(0.0)
    return gs


def load_all_phrases(dirname,filter="*"):
    all_phrases=[]
    filter_dirs=re.compile(filter)
    for filename in os.listdir(dirname):
        if not filter_dirs.search(filename):
            continue
        phrases=load_phrases_from_file(dirname,filename)
        if len(phrases)>0:
            all_phrases.append((filename,phrases))
    return all_phrases

def load_all_gs(dirname):
    all_gs=[]
    for filename in os.listdir(dirname):
        gs=load_gs_from_file(dirname,filename)
        if len(gs)>0:
            all_gs.append((filename,gs))
    return all_gs


def eval(cmd,filename_gs,filename_sys):
    cmd=cmd+[filename_gs,filename_sys]    
    p = Popen(cmd,  stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    res=stdout.replace('Pearson: ','').strip()    
    return float(res)


def infer_test_file(dirname_gs,filename_sys):
    filename=os.path.basename(filename_sys)
    bits=filename.split('.')
    h,t=os.path.split(dirname_gs)
    h,year=os.path.split(h)
    filename_gs=os.path.join(dirname_gs,
                bits[0]+'.'+year+'.gs.'+bits[2]+'.txt'
        )
    return filename_gs


def eval_all(cmd,dirname_gs,filenames):
    res=[]
    total=[]
    with tempfile.NamedTemporaryFile() as file_gs, tempfile.NamedTemporaryFile() as file_sys:             
        for filename_sys in filenames:
            filename_gs = infer_test_file(dirname_gs,filename_sys)
            res.append((os.path.basename(filename_sys),eval(cmd,filename_gs,filename_sys)))
            total.append(res[-1][1])
            with open(filename_sys) as infile:
                for line in infile:
                    file_sys.write(line)
            with open(filename_gs) as infile:
                for line in infile:
                    file_gs.write(line)
        ##res.append(('All',eval(cmd, file_gs.name, file_sys.name)))
        res.append(('Mean',np.mean(total)))
    return res


def train_model_srv(train_gs, train_output,args={'kernel':'linear'}):    
    svr_lin = SVR(**args)

    score_gs=[]
    score_out=[]
    for x in train_gs.keys():
        if train_gs.has_key(x) and train_output.has_key(x):
            score_gs.extend(train_gs[x])
            score_out.extend(train_output[x])

    score_out=np.nan_to_num(score_out)

    svr_lin.fit([x for x in score_out], score_gs)
    
    return svr_lin    

def preprocessing_nltk_tokenise(phrase):
    return word_tokenize(phrase)
