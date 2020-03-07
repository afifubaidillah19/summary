import numpy as np

class Cosine:
    def __init__(self):
        super().__init__()

    def cosine(self, doc1, doc2):
        result = []
        for d1 in doc1:
            if(np.dot(np.linalg.norm(doc1), np.linalg.norm(np.array(doc2).T)) == 0):
                result.append(0)
            else:
                temp = np.dot(d1, doc2)
                temp = temp/np.dot(np.linalg.norm(doc1), np.linalg.norm(np.array(doc2).T))
                result.append(temp)
        return result