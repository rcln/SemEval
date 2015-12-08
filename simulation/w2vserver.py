#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Flask web service for word2vec infor
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

from flask import Flask, request
from gensim.models.word2vec import Word2Vec
import codecs
import json
import argparse


app = Flask('w2vserver')

@app.route('/',methods=['GET'])
def index():
    return "Service up" 

@app.route('/api/v0.1/get',methods=['POST'] )
def get():
    data=request.get_json(silent=True)
    words=data['words']
    vecs=[]
    for word in words:
        try:
            vecs.append(model[word].tolist())
        except:
            vecs.append([0.0 for x in range(300)])
    return json.dumps({"vectors":vecs,'words':words},ensure_ascii=False) 
    

if __name__ == '__main__':
    p = argparse.ArgumentParser("Author identification")
    p.add_argument("--model",default='data/GoogleNews-vectors-negative300.bin', type=str,
                action="store", dest="model",
                help="Word2vec model to use")
    p.add_argument("--host",default="127.0.0.1",
            action="store", dest="host",
            help="Root url [127.0.0.1]")
    p.add_argument("--port",default=5000,type=int,
            action="store", dest="port",
            help="Port url [500]")
    p.add_argument("--debug",default=False,
            action="store_true", dest="debug",
            help="Use debug deployment [Flase]")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    model = Word2Vec.load_word2vec_format(opts.model, binary=True)

    app.run(debug=opts.debug,
            host=opts.host,
            port=opts.port)

