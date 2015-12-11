from scipy.spatial.distance import cosine
import numpy as np

# Calculates de distance by summing all word vectors
def vector_sum(model,phr):
    acc1=np.zeros(300)
    nacc1=0
    for word in phr:
        try:
            acc1+=model[word]
            nacc1+=1
        except KeyError:
            pass
    if nacc1>0:
        return acc1/nacc1
    else:
        return np.zeros(300)

# Calculates de distance by summing all word vectors
def distances_cosine(vec1,vec2):
    return cosine(vec1,vec2)

