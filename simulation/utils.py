#!/usr/bin/env python
# -*- coding: utf-8
import os
import re

re_file=re.compile('.*\.input\..*\.txt$')
re_gs=re.compile('.*\.gs\..*\.txt$')

def load_phrases_from_file(dirname,filename):
    phrases=[]
    if not re_file.match(filename):
        return []

    with open(os.path.join(dirname,filename)) as data:
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


def load_all_phrases(dirname):
    all_phrases=[]
    for filename in os.listdir(dirname):
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


