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
import os.path
from math import sqrt


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


def eval_all_local(cmd,dirname_gs,filenames,standout_threshold):
    res=[]
    total=[]
    with tempfile.NamedTemporaryFile() as file_gs, tempfile.NamedTemporaryFile() as file_sys:             
        for filename_sys in filenames:
            filename_gs = infer_test_file(dirname_gs,filename_sys)
            res.append((os.path.basename(filename_sys),eval_local(cmd,filename_gs,filename_sys)))
            total.append(res[-1][1])
            if standout_threshold != 0.0:
                analyze_pairs(filename_gs,filename_sys, standout_threshold)
            with open(filename_sys) as infile:
                for line in infile:
                    file_sys.write(line)
            with open(filename_gs) as infile:
                for line in infile:
                    file_gs.write(line)
        ##res.append(('All',eval(cmd, file_gs.name, file_sys.name)))
        print res
        res.append(('Mean',np.mean(total)))
    return res

def eval_local(cmd,file_gs, file_sys):
    filtered=[]
    a=[]
    b=[]
    c=[]

    i_gs=0
    i=0
    with open(file_gs) as gs:
        for score in gs:
            if len(score.strip())==0:
                filtered.append(1)
            else:
                filtered.append(0)
                a.append(float(score))
                i+=1
                # print str(i) + "-I->" + score.strip()
            i_gs+=1
        
    i_gs=0
    j=0 
    with open(file_sys) as sys:
        for score in sys:
            if not filtered[i_gs] :
                b.append(float(score))
                c.append(float(100.00))
                j+=1                
                # print str(j) + "-O->" + score.strip()
            i_gs+=1

    if j>0:
        sumw=0

        sumwy=0;
        for x in xrange(1,10):
            pass
        for y in xrange(0, i-1):
            sumwy = sumwy + (100 * a[y])
            sumw = sumw + 100
        meanyw = sumwy/sumw

        sumwx=0
        for x in xrange(0, i-1):        
            sumwx = sumwx + (c[x] * b[x])       
        meanxw = sumwx/sumw

        sumwxy = 0
        for x in xrange(0, i-1):        
            sumwxy = sumwxy + c[x]*(b[x] - meanxw)*(a[x] - meanyw)      
        covxyw = sumwxy/sumw

        sumwxx = 0
        for x in xrange(0, i-1):        
            sumwxx = sumwxx + c[x]*(b[x] - meanxw)*(b[x] - meanxw)
        covxxw = sumwxx/sumw

        sumwyy = 0
        for x in xrange(0, i-1):        
            sumwyy = sumwyy + c[x]*(a[x] - meanyw)*(a[x] - meanyw)  
        covyyw = sumwyy/sumw

        corrxyw = covxyw/sqrt(covxxw*covyyw)
        
        return float("{0:.4f}".format(corrxyw))


# standout_threshold = if negative stand out phrase pairs which scores differences are lesser than ..
# standout_threshold = if positive stand out phrase pairs which scores differences are bigger than ..
def analyze_pairs(file_gs, file_sys, standout_threshold):
    if standout_threshold==0.0:
        return

    filtered=[]
    a=[]
    b=[]
    c=[]
    idx=[]
    logs=[]

    i_gs=0
    i=0
    with open(file_gs) as gs:
        for score in gs:
            if len(score.strip())==0:
                filtered.append(1)
            else:
                filtered.append(0)
                a.append(float(score))
                idx.append(i_gs)
                i+=1
                # print str(i) + "-I->" + score.strip()
            i_gs+=1
        
    i_gs=0
    j=0 
    file_log=file_sys[:-3]+"log"
    if os.path.isfile(file_log):
        with open(file_sys) as sys, open(file_log) as flog:
            for score, log in zip(sys, flog):
                if not filtered[i_gs] :
                    b.append(float(score))
                    c.append(float(100.00))
                    logs.append(log)
                    j+=1                
                    # print str(j) + "-O->" + score.strip()
                i_gs+=1        
    else:
        with open(file_sys) as sys:
            for score in sys:
                if not filtered[i_gs] :
                    b.append(float(score))
                    c.append(float(100.00))
                    j+=1                
                    # print str(j) + "-O->" + score.strip()
                i_gs+=1

    if j>0:
        print "\n\n\n************ Analizing file :: {0} **************\n\n\n".format(file_sys)
        outliers=0
        for x in xrange(0, i-1):
            report=0
            diff=abs(a[x]-b[x])            
            if standout_threshold>0.0:
                if diff > abs(standout_threshold):
                    report=1
            else:
                if diff < abs(standout_threshold):
                    report=1

            if report:
                # txt = str(idx[x]) + "-->" + str(a[x]) + "<>" + str(b[x])
                outliers +=1
                txt = str(a[x])
                if logs:
                    txt +=  "-->" + logs[x]
                print txt
        if standout_threshold > 0.0:
            print "[{0:1d}] phrase pairs with score differences > {1:1.1f}".format(outliers, standout_threshold)
        else:
            print "[{0:1d}] phrase pairs with score differences < {1:1.1f}".format(outliers, standout_threshold)
