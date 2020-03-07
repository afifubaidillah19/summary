import numpy as np

class VSM:
    def __init__(self):
        pass

    def list_term(self, listterm):
        tc = []
        for term in listterm:
            tc.extend(term)
        return list(set(tc))

    def cal_tf(self, doc, termcollections):
        result = []
        for d in doc:
            doc_result = []
            for term in termcollections:
                doc_result.append(d.count(term))
            result.append(doc_result)
        return result

    def cal_tf_basic(self, doc, termcollections):
        doc_result = []
        for term in termcollections:
            doc_result.append(doc.count(term))
        return doc_result

    def cal_df(self, doc, termcollections):
        result = []
        for term in termcollections:
            d = 0
            for dc in doc:
                if term in dc:
                    d +=1
            if d == 0:
                d = 1
            result.append(np.log(len(doc)/d))
        return result

    def cal_tf_normalize(self, doc):
        result = []
        for d in doc:
            tf = np.log(1+ np.asarray(d))
            result.append(tf)
        return result

    def cal_vsm(self, tf, idf):
        result = []
        for doc in tf:
            idf_i = []
            for i in range(len(doc)):
                idf_i.append(doc[i] * idf[i])
            result.append(idf_i)
        return result

    def cal_vsm_basic(self, tf, idf):
        result = []
        for i in range(len(tf)):
            result.append(tf[i] * idf[i])
        return result;


                
                