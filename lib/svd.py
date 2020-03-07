import numpy as np
import math
from numpy import diag
from numpy import dot
from numpy import zeros
from lib.cosine import Cosine

class SVD:
    def __init__(self):
        pass

    def cal_svd(self, weight, weight_judul):
        # ubah dari d x t jadi t x d
        A = np.array(weight).T
        AT = A.T
        cosine = Cosine()

        cos = cosine.cosine(weight, weight_judul)
        
        cosAvg = np.average(cos)

        AAT = np.dot(A, AT)
        ATA = np.dot(AT, A)

        eignValAAT, eignVecAAT = np.linalg.eig(AAT)
        eignValATA, eignVecATA = np.linalg.eig(ATA)

        U = eignVecAAT
        V = eignVecATA
        VT = V.T

        S = np.zeros((len(eignValATA), len(eignValATA)))
        for i in range(len(eignValATA)):
            S[i][i] = eignValATA[i]
        S = np.sqrt(S)

        length = []
        for i in range(len(VT)):
            sigma = 0
            for j in range(len(V[i])):
                sigma += V[i][j] * S[j][j]
            length.append(np.sqrt(abs(sigma)))
        
        average = np.average(length)
        index_sentence = []
        for i in range(len(length)):
            if(length[i] >= average):
                index_sentence.append(i)

        return index_sentence
            

        



