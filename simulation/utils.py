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
from itertools import izip
from fill_w2v import *
from fill_samsung_owl import *


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


def load_all_phrases(dirname,filter="."):
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


def eval_all(cmd,dirname_gs,filenames,opts={}):
    res=[]
    total=[]
    if opts.verbose:
        with open(opts.model,'rb') as idxf:
            model = pickle.load(idxf)
    filter_dirs=re.compile(opts.filter_test)
    with tempfile.NamedTemporaryFile() as file_gs, tempfile.NamedTemporaryFile() as file_sys:             
        for filename_sys in filenames:
            if not filter_dirs.search(filename_sys):
                    continue
            filename_gs = infer_test_file(dirname_gs,filename_sys)
            eval_res=eval(cmd,filename_gs,filename_sys)
            print u"{0:<40}: {1:<1.4f}".format(os.path.basename(filename_sys),eval_res)
            total.append(eval_res)
            with open(filename_sys) as infile:
                for line in infile:
                    file_sys.write(line)
            with open(filename_gs) as infile:
                for line in infile:
                    file_gs.write(line)
            try:
                opts.diff
                analyse(filename_sys,filename_gs,model,opts=opts)
            except AttributeError:
                pass
        print u"{0:<40}: {1:<1.4f}".format('All',eval(cmd, file_gs.name, file_sys.name))
        print u"{0:<40}: {1:<1.4f}".format('Mean',np.mean(total))
    return res

def analyse(filename_sys,filename_gs,model,opts={}):
    res=[]
    dirname_gs,basename_gs=os.path.split(filename_gs)
    phrases=load_phrases_from_file(
        dirname_gs,
        basename_gs.replace('gs','input')
    )
    with open(filename_sys) as fsys, open(filename_gs) as fgs:
        for idx,(line1,line2) in enumerate(izip(fsys,fgs)):
            line1=line1.strip()
            line2=line2.strip()
            if len(line2)>0:
                gs=float(line2)
            else:
                gs=0.0
            if len(line1)>0:
                sys=float(line1)
            else:
                sys=0.0
            if abs(gs-sys)> opts.diff:
                phrs=phrases[idx]
                phr1,phr2=preprocessing(phrs[0],phrs[1],opts=opts)
                num=sts(model,phr1,phr2,opts=opts)
                res.append((phrs,(num,gs),num))
                print u"SYS:", sys, u"GS:", gs
                print u"DISTANCE",", ".join([str(x) for x in num]) 
                print u"Phrase 1:",phrs[0]
                print u"Phrase 2:",phrs[1]
                print u"Align  1:"
                aligns=align(model,phr1,phr2,opts=opts)
                for a in aligns:
                    print u"  {0:<30}, {1:<30} :  {2:<1.4f}".format(*a)
                print u"Align  2:"
                aligns=align(model,phr2,phr1,opts=opts)
                for a in aligns:
                    print u"  {0:<30}, {1:<30} :  {2:<1.4f}".format(*a)
                print u"--"

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
