
# coding: utf-8

# # Notebook para STS 2017
# 
# Experimentos de evaluación y etiquetado de datos

# In[1]:

import time
import os
import random
import re
import codecs
import numpy as np
from collections import Counter

def verbose(*args):
    print(" ".join([str(a) for a in args]))

class Opts:
    verbose=False
    filter_test=".*"
    
opts=Opts()


# # Código para EMBEDINGS
# 
# Este código carga los embeddings de Glove y declara una función para crear la matrix sincronizada despues
# 
# * 0 para padding
# * 1 para inición de oración
# * 2 Para palabras desconocidas (OOV)
# * 3 inicia la numeración de palabras

# In[2]:

EMBEDDING_DIM=300
GLOVE_DIR='.'
embeddings_index = {}
f = open(os.path.join(GLOVE_DIR, 'glove.6B.'+str(EMBEDDING_DIM)+'d.txt'))
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()

print('Found %s word vectors.' % len(embeddings_index))
embeddings_index['###'] = np.zeros(100)

def create_embedding_matrix(word_index,edim,embeddings_index,nb_words):
    # prepare embedding matrix
    embedding_matrix = np.zeros((nb_words + 4, edim))
    for word, i in word_index.items():
        if i > MAX_NB_WORDS:
            continue
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            embedding_matrix[i+3] = embedding_vector

    return embedding_matrix


# # Diferentes funciones para cargar datos STS1

# In[3]:

def load_phrases_from_file(dirname,filename,format='2017',translation=False):
    re_file=re.compile('.*\.input\..*\.txt$')                                        
    re_file_translation=re.compile('.*\.input\..*\.translation.txt$')
    
    if translation:                                                              
        re_file=re_file_translation
        
    phrases=[]                                                                   
    if not re_file.match(filename):                                              
        return []                                                                
    with codecs.open(os.path.join(dirname,filename),encoding='utf-8') as data:
        for line in data:
            bits=line.strip().split('\t')
            if len(bits)>=2 or len(bits)<=4:                                     
                if not format:                                                   
                    phrases.append((bits[0],bits[1]))                            
                elif format=="2017":                                             
                    phrases.append((bits[0],bits[1]))
    return phrases 

def load_gs_from_file(dirname,filename,format=None):
    re_gs=re.compile('.*\.gs\..*\.(txt|ascii)$')
    re_file_translation=re.compile('.*\.input\..*\.translation.txt$')
    gs=[]
    if not format:
        if not re_gs.match(filename):
            return []
    elif format=="2017":
        if not re_file_translation.match(filename):
            return []

    with open(os.path.join(dirname,filename)) as data:
        for line in data:
            line=line.strip()
            try:
                if not format:
                    gs.append(float(line))
                elif format=="2017":
                    bits=line.strip().split('\t')
                    if len(bits)>=2 or len(bits)<=4:                                                                                    
                        gs.append(float(bits[1])) 
            except ValueError:
                gs.append(None)
    return gs

def load_all_phrases(dirname,filter=".",format=None,translation=False):          
    all_phrases=[]                                                               
    filter_dirs=re.compile(filter)
    for filename in os.listdir(dirname):
        if not filter_dirs.search(filename):                                     
            continue
        phrases=load_phrases_from_file(dirname,filename,format=format,translation=translation)
        if len(phrases)>0: 
            all_phrases.append((filename,phrases))                               
    return all_phrases

def load_all_gs(dirname,format=None):
    all_gs=[]
    for filename in os.listdir(dirname):
        gs=load_gs_from_file(dirname,filename,format=format)
        if len(gs)>0:
            all_gs.append((filename,gs))
    return all_gs

def load_train_dirs(dirs,dir="train"):
    train_data=[]
    gs_data=[]
    for directory,format,translation in dirs: 
        verbose('Starting load '+dir+'ing',directory)
        train_data_=load_all_phrases(os.path.join(directory,dir),format=format,translation=translation)
        gs_data_=dict(load_all_gs(os.path.join(directory,dir),format=format))
        for (n,d) in train_data_:
            if not format:
                n_=n.replace('input', 'gs')
            else:
                n_=n
            if translation and not format:
                n_=n_.replace('.translation', '')
            for i,s in enumerate(d):
                if gs_data_[n_][i]:
                    train_data.append(s[0])
                    train_data.append(s[1])
                    gs_data.append(gs_data_[n_][i])
            verbose("Phrases in",n,len(d),len(gs_data_[n_]))
        verbose('Total train phrases',directory,sum([len(d) for n,d in train_data_]))
        verbose('Total train phrases',len(train_data))
    return train_data,gs_data

def infer_test_file(dirname_gs,filename_sys):
    filename=os.path.basename(filename_sys)
    bits=filename.split('.')
    h,t=os.path.split(dirname_gs)
    h,year=os.path.split(h)
    filename_gs=os.path.join(dirname_gs,
                bits[0]+'.'+year+'.gs.'+bits[3]+'.txt'
        )
    return filename_gs


def load_test_dirs(dirs,dir="test"):
    train_data={}
    gs_data=[]
    gs_files={}
    for directory,format,translation in dirs:
        verbose('Starting loading test',directory,translation)
        train_data_=load_all_phrases(os.path.join(directory,'test'),format=format,translation=translation)
        for n,d in train_data_:
            train_data[n]=[]
            gs_files[n]=infer_test_file(os.path.join(directory,'test'),n)
            for i,s in enumerate(d):
                train_data[n].append(s[0])
                train_data[n].append(s[1])
            verbose("Total phraes in",n,len(d))
        verbose('Total test phrases',directory,sum([len(d) for n,d in train_data_]))
    return train_data,gs_files
        
def prepare_data_concatenation(data_,gs_=None,test=False):
    train_data=[]
    for i in range(int(len(data_)/2)):
        train_data.append(data_[i*2]+" ### "+data_[i*2+1])
        #if not test:
        #    train_data.append(data_[i*2+1]+" ### "+data_[i*2])
    if not gs_:
        return train_data
    else:
        gs_data=[]
        for i in range(len(gs_)):
            gs_data.append(gs_[i])
            if not test:
                gs_data.append(gs_[i])
        return train_data,gs_data

import re
punct=re.compile(r"([,.?\)\(!-;\"'])")

def prepare_sentence(sntc):
    return punct.sub(" punt\\1 ",sntc)
    
    
def prepare_data_separated(data_,gs_=None,test=False):
    train_data1=[]
    train_data2=[]
    for i in range(int(len(data_)/2)):
        train_data1.append(prepare_sentence(data_[i*2]))
        train_data2.append(prepare_sentence(data_[i*2+1]))
        if not test:
            train_data1.append(prepare_sentence(data_[i*2+1]))
            train_data2.append(prepare_sentence(data_[i*2]))
    if not gs_:
        return train_data1,train_data2
    else:
        gs_data=[]
        for i in range(len(gs_)):
            gs_data.append(gs_[i])
            if not test:
                gs_data.append(gs_[i])
        return train_data1,train_data2,gs_data


# # Declaración de variables
# 
# Dos secciones E para evaluación con datos de 2016 y data 2017

# In[4]:

EYEAR="2016"
YEAR="2017"
ETRAIN_DIRS=[
    ("../english_testbed/data/"+EYEAR,None,False)]

ETEST_DIRS=[
    ("../english_testbed/data/"+EYEAR,None,False)]


TRAIN_DIRS=[
    ("../arabic_testbed/data/"+YEAR,"2017",True),
    ("../english_arabic_testbed/data/"+YEAR,"2017",True),
    ("../english_spanish_testbed/data/"+YEAR,None,True),
    ("../english_testbed/data/"+YEAR,None,False),
    ("../spanish_testbed/data/"+YEAR,None,True),
    ]
TEST_DIRS=[
    ("../arabic_testbed/data/"+YEAR,"2017",True),
    ("../english_arabic_testbed/data/"+YEAR,"2017",True),
    ("../english_spanish_testbed/data/"+YEAR,None,True),
    ("../english_testbed/data/"+YEAR,None,False),
    ("../english_turkish_testbed/data/"+YEAR,"2017",True),
    ("../spanish_testbed/data/"+YEAR,None,True),
]

GS_FILES={}


# # Carga training para evaluación (desarrollo)

# In[5]:

# LOADING EVALUATION TRAINING
etrain_data_,egs_data_=load_train_dirs(ETRAIN_DIRS)

print("Avg size:",np.mean([len(x.split()) for x in etrain_data_]))
print("Max size:",np.max([len(x.split()) for x in etrain_data_]))
print("Min size:",np.min([len(x.split()) for x in etrain_data_]))

etrain_data1,etrain_data2,egs_data=prepare_data_separated(etrain_data_,egs_data_)
    
print("Avg size after merging:",np.mean([len(x.split()) for x in etrain_data1]))
print("Max size after merging:",np.max([len(x.split()) for x in etrain_data1]))
print("Min size after merging:",np.min([len(x.split()) for x in etrain_data1]))
print("Total examples",len(etrain_data1))
print("Total labels",len(egs_data))


# # Carga test para evaluación (desarrollo)

# In[6]:

# LOADING EVALUATION TESTING
etest_data_, egs_files=load_test_dirs(ETEST_DIRS,dir="test")
    
print("Total evaluating files",len(etest_data_))
print("Total candidates gs files",len(egs_files))


# # Carga datos de entrenamiento (2017)

# In[7]:

# LOADING TRAINING
train_data_,gs_data_=load_train_dirs(TRAIN_DIRS)

print("Avg size:",np.mean([len(x.split()) for x in train_data_]))
print("Max size:",np.max([len(x.split()) for x in train_data_]))
print("Min size:",np.min([len(x.split()) for x in train_data_]))

train_data1,train_data2,gs_data=prepare_data_separated(train_data_,gs_data_)
    
print("Avg size after merging:",np.mean([len(x.split()) for x in train_data1]))
print("Max size after merging:",np.max([len(x.split()) for x in train_data1]))
print("Min size after merging:",np.min([len(x.split()) for x in train_data1]))
print("Total examples",len(train_data1))
print("Total labels",len(gs_data))


# # Carga datos de prueba 2017

# In[8]:

test_data_, gs_files =load_test_dirs(TEST_DIRS)
print("Total examples",len(test_data_))


# # Función para preparar secuencias en Keras

# In[9]:

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical

MAX_NB_WORDS=15000
MAX_SEQUENCE_LENGTH=30
VALIDATION_SPLIT=0.1
LSTM_DIM=100

def texts_to_sequences(word_index,nb_words,xs):
    nb_words = min(nb_words, len(word_index))
    xs_=[]
    for x in xs:
        x_=[1]
        for w in x.lower().split():
            i=word_index.get(w)
            if i: 
                if i>nb_words:
                    x_.append(2)
                else:
                    x_.append(i+3)
            else:
                x_.append(2)
        xs_.append(x_)
    return xs_,nb_words
    
def skipodd(vals):
    return vals[range(0,vals.shape[0],2)]
        
def prepare_keras_data(train_data1,train_data2,validation_split=VALIDATION_SPLIT,tokenizer=None,gs_data=None,nb_words=None):
    print('Shape of data1 tensor:', len(train_data1))
    print('Shape of data2 tensor:', len(train_data2))
    if not tokenizer:
        tokenizer = Tokenizer(nb_words=nb_words)
        tokenizer.fit_on_texts(train_data1+train_data2)
    word_index = tokenizer.word_index
    print('Found %s unique tokens.' % len(word_index))
    
    sequences1,nb_words = texts_to_sequences(word_index,MAX_NB_WORDS,train_data1)
    sequences2,nb_words = texts_to_sequences(word_index,MAX_NB_WORDS,train_data2)
    print("Avg seq 1",np.mean([len(seq) for seq in sequences1]))
    print("Avg seq 2",np.mean([len(seq) for seq in sequences2]))
    print("Max seq 1",np.max([len(seq) for seq in sequences1]))
    print("Max seq 2",np.max([len(seq) for seq in sequences2]))   
    
    data1 = pad_sequences(sequences1, maxlen=MAX_SEQUENCE_LENGTH)
    data2 = pad_sequences(sequences2, maxlen=MAX_SEQUENCE_LENGTH)
    #data=np.zeros((data_.shape[0]/2,data_.shape[1]*2))
    #for i in range(data_.shape[0]/2):
    #    data[i,:data_.shape[1]]=data_[2*i]
    #    data[i,data_.shape[1]:]=data_[2*i+1]

    print('Shape of data1 tensor:', data1.shape)
    print('Shape of data2 tensor:', data2.shape)
    if gs_data:
        print(gs_data[:10])
        #labels = to_categorical(np.asarray(gs_data))
        labels = np.asarray(gs_data)
        print('Shape of label tensor:', labels.shape)

    
    if validation_split!= 0.0:
        # split the data into a training set and a validation set
        indices_ = np.arange(int(data1.shape[0]/2))
        np.random.shuffle(indices_)
        indices=[]
        for i in indices_:
            indices.append(2*indices_[i])
            indices.append(2*indices_[i]+1)
        print("Indices",indices[:10])
        data1 = data1[indices]
        data2 = data2[indices]
        if gs_data:
            labels = labels[indices]
        nb_validation_samples = int(validation_split * data1.shape[0])
        indices_ = np.arange(len(data1)-nb_validation_samples)
        np.random.shuffle(indices_)
        x1_train = data1[:-nb_validation_samples][indices_]
        x2_train = data2[:-nb_validation_samples][indices_]
        y_train = labels[:-nb_validation_samples][indices_]
        x1_val = skipodd(data1[-nb_validation_samples:])
        x2_val = skipodd(data2[-nb_validation_samples:])
        y_val = skipodd(labels[-nb_validation_samples:])

        print('Shape of X1 train:',x1_train.shape)
        print('Shape of X2 train:',x2_train.shape)
        print('Shape of y train:',y_train.shape)
        print('Shape of X1 test :',x1_val.shape)
        print('Shape of X2 test :',x2_val.shape)
        print( 'Shape of y test :',y_val.shape)
    
        return x1_train,x2_train,y_train,x1_val,x2_val,y_val, word_index, tokenizer, nb_words
    else:
        x1_train = data1
        x2_train = data2
        print('Shape of X1 train:'),x1_train.shape
        print('Shape of X2 train:'),x2_train.shape
        return x1_train,x2_train, word_index, tokenizer, nb_words
        


# # Llamado a funicón para preparar datos

# In[10]:

x1_etrain,x2_etrain,y_etrain,x1_eval,x2_eval,y_eval, eword_index, etok, nb_ewords =    prepare_keras_data(etrain_data1,etrain_data2,gs_data=egs_data,nb_words=MAX_NB_WORDS)


# # Llamado de función para preparar matrix de datos de embedding

# In[11]:

ematrix=create_embedding_matrix(eword_index,EMBEDDING_DIM,embeddings_index,nb_ewords)
print("Embedding matrix evaluation", ematrix.shape)
#ematrix= np.zeros((nb_ewords + 4, EMBEDDING_DIM))


# # Modelo de STS en keras

# In[12]:

from keras.layers import Embedding,Merge, merge, RepeatVector
from keras.layers import Dense, Input, Flatten, Dropout, Permute
from keras.layers import Conv1D, MaxPooling1D, Embedding, TimeDistributed, TimeDistributedDense
from keras.models import Model
from keras.regularizers import l2
from keras.models import Sequential
from keras.layers import LSTM,Bidirectional, Flatten, Lambda, MaxoutDense, Activation, Reshape, Dropout, ActivityRegularization
from keras.optimizers import SGD
from keras.layers.advanced_activations import PReLU
from keras.layers.core import *

def get_R(X):
    Y, alpha = X[0], X[1]
    ans = K.T.batched_dot(Y, alpha)
    return ans


def create_model(word_index,matrix,nb_words):
    
    sA_input     = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32', name='sA_input')
    sA_embedding = Embedding(nb_words + 4,
                           EMBEDDING_DIM,
                            weights=[matrix],
                            dropout=0.2,
                            trainable=False)(sA_input)
    sA_BLSTM = Bidirectional(LSTM(LSTM_DIM,
                    dropout_W=0.2,return_sequences=True,
                    dropout_U=0.2))(sA_embedding)            

    sB_input     = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32', name='sB_input')
    sB_embedding = Embedding(nb_words + 4,
                           EMBEDDING_DIM,
                            weights=[matrix],
                            dropout=0.2,
                            trainable=False)(sB_input)
    sB_BLSTM = Bidirectional(LSTM(LSTM_DIM,
                    dropout_W=0.2,#return_sequences=True,
                    dropout_U=0.2))(sB_embedding)       
    
    sA = sA_BLSTM
    sB = sB_BLSTM
    
    h_n = sB_BLSTM
    Y = sA_BLSTM
    k= 2*LSTM_DIM
    L= MAX_SEQUENCE_LENGTH
    Whn = Dense(2*LSTM_DIM, W_regularizer=l2(0.01), name="Wh_n")(h_n)
    Whn_x_e = RepeatVector(L, name="Wh_n_x_e")(Whn)
    WY = TimeDistributed(Dense(k, W_regularizer=l2(0.01)), name="WY")(Y)
    merged = merge([Whn_x_e, WY], name="merged", mode='sum')
    M = Activation('tanh', name="M")(merged)

    
    alpha_ = TimeDistributed(Dense(1, activation='linear'), name="alpha_")(M)
    flat_alpha = Flatten(name="flat_alpha")(alpha_)
    alpha = Dense(L, activation='softmax', name="alpha")(flat_alpha)

    Y_trans = Permute((2, 1), name="y_trans")(Y)  # of shape (None,300,20)

    r_ = merge([Y_trans, alpha], output_shape=(k, 1), name="r_", mode=get_R)

    r = Reshape((k,), name="r")(r_)

    Wr = Dense(k, W_regularizer=l2(0.01))(r)
    Wh = Dense(k, W_regularizer=l2(0.01))(h_n)
    merged = merge([Wr, Wh], mode='sum')
    h_star = Activation('tanh')(merged)
    
    
    #similarity.add(Dense(1))
    #similarity.add(Activation('linear'))
    #maxout = MaxoutDense(300)(pair_sent)
    output = MaxoutDense(1)(h_star)
    
    
    similarity = Model(input=[sA_input,sB_input], output=output)
    similarity.compile(loss='mean_absolute_error', optimizer='rmsprop', metrics=['mean_absolute_error','mean_squared_error'])
    #similarity.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    print(similarity.summary())

    
    #model = Sequential()
    #model.add(embedding_layer)
    #model.add(Conv1D(128,5,activation='relu'))
    #model.add(Conv1D(32,3,activation='relu'))
    #model.add(MaxPooling1D(5))
    #model.add(Dropout(0.2))
    #model.add(Bidirectional(LSTM(100, dropout_W=0.2, dropout_U=0.2)))
    #model.add(Dense(6, activation='softmax'))
    #model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    #print(model.summary())
    return similarity,sA,sB


# # Creación de modelo para evaluación (desarrollo)

# In[ ]:

import gc
for i in range(3): gc.collect()
# happy learning!
model,p1,p2 = create_model(eword_index,ematrix,nb_ewords)


# # Entrenamiento para evaluación (desarrollo)

# In[ ]:

model.fit([x1_etrain,x2_etrain], y_etrain, validation_data=([x1_eval,x2_eval], y_eval),
          nb_epoch=20, batch_size=128)


# # Evaluación sobre datos de prueba (2016 inglés)

# In[15]:

# EVALUATING
cmd=["perl",
    "../english_testbed/data/2015/evaluate/correlation-noconfidence.pl"]
from subprocess import Popen, PIPE, STDOUT

def eval_tmp(cmd,filename_gs,filename_sys): 
    cmd=cmd+[filename_gs,filename_sys]     
    p = Popen(cmd,  stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    res=stdout.decode("utf-8") 
    res=res.replace('Pearson: ','').strip()
    return float(res)

for dir,data in etest_data_.items():
    print("Evaluating",dir,len(data))
    data1,data2=prepare_data_separated (data,test=True)
    print("Size data1",len(data1))
    print("Size data2",len(data2))
    print(data1[28])
    print(data2[28])
    x1_test_eval,x2_test_eval, eword_index, etok, _ = prepare_keras_data(data1,data2,tokenizer=etok, validation_split=0.0)
    print("Size data",len(data1))
    print(x1_test_eval[4])
    print(x2_test_eval[4])
    res=model.predict([x1_test_eval,x2_test_eval])
    res=np.clip(res,0,5)
    #res=[np.argmax(x) for x in res]
    print(res[:10])
    filename=os.path.join('.',dir)
    fn=open(filename,'w')
    for num in res:
        print( "{0:1.1f}".format(num[0]),file=fn)
    fn.close()
    print(eval_tmp(cmd,egs_files[dir],filename))


# # Se preparan datos para training (2017)

# In[16]:

print("Loading data for trainig")
x1_train,x2_train,y_train,x1_val,x2_val,y_val, word_index, tok, nb_words =    prepare_keras_data(train_data1,train_data2,gs_data=gs_data,nb_words=MAX_NB_WORDS)

matrix=create_embedding_matrix(word_index,EMBEDDING_DIM,embeddings_index,nb_words)
print("Embedding matrix evaluation", ematrix.shape)


# # Se carga modelo y se entrena con (2017)

# In[17]:

print("Trainig")
import gc
for i in range(3): gc.collect()
# happy learning!
model_final,_,_ = create_model(word_index,matrix,nb_words)

model_final.fit([x1_train,x2_train], y_train, validation_data=([x1_val,x2_val], y_val),
          nb_epoch=250, batch_size=1024)


# # Se etiquetan los datos

# In[18]:

for dir,data in test_data_.items():
    print("Evaluating",dir,len(data))
    data1_test,data2_test=prepare_data_separated (data,test=True)
    print("Size data1",len(data1_test))
    print("Size data2",len(data2_test))
    print("Sntc 30:",data1_test[30])
    print("Sntc 30:",data2_test[30])
    x1_test,x2_test, word_index, tok, _ = prepare_keras_data(data1_test,data2_test,tokenizer=tok, validation_split=0.0)
    res=model.predict([x1_test_eval,x2_test_eval])
    print("Sequence 30:",x1_test[30])
    print("Sequence 30:",x2_test[30])
    res=model.predict([x1_test,x2_test])
    res=np.clip(res,0,5)
    #res=[np.argmax(x) for x in res]
    print(res[:10])
    filename=os.path.join('.',dir)
    fn=open(filename,'w')
    for num in res:
        print( "{0:1.1f}".format(num[0]),file=fn)
    fn.close()


# 
