import numpy as np

# Calculates de distance by summing all word vectors
def vector_sum(model,phr):
    acc1=np.zeros(300)
    nacc1=0
    for word in phr:
        try:
            acc1+=model[word]
        except:
            acc1+=np.zeros(300)+0.25
        nacc1+=1
    if nacc1>0:
        return acc1/nacc1
    else:
        return np.zeros(300)




