import os
import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk import sent_tokenize
import re

class Preprocessing:
    def __init__(self):
        self.path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data'))
        pass

    def read_file(self):
        texts = []
        fileNames = []
        for filename in os.listdir(self.path):
            fileNames.append(filename)
        
        fileNames.sort(key=lambda f: int(re.sub('\D', '', f)))
        
        texts = []

        for r, d, files in os.walk(self.path):
            for f in fileNames:
                text = open(os.path.join(r, f), 'r', encoding="utf-8-sig").read()
                texts.append(text)
        return texts

    def read_title(self):
        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'judul'))
        fileNames = []
        for filename in os.listdir(path):
            fileNames.append(filename)
        
        fileNames.sort(key=lambda f: int(re.sub('\D', '', f)))
        
        texts = []

        for r, d, files in os.walk(path):
            for f in fileNames:
                text = open(os.path.join(r, f), 'r', encoding="utf-8-sig").read()
                texts.append(text)
        return texts

    def read_ringkas(self):
        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'dataset'))
        fileNames = []
        for filename in os.listdir(path):
            fileNames.append(filename)
        
        fileNames.sort(key=lambda f: int(re.sub('\D', '', f)))
        
        texts = []

        for r, d, files in os.walk(path):
            for f in fileNames:
                text = open(os.path.join(r, f), 'r', encoding="utf-8-sig").read()
                texts.append(text)
        return texts

    def read_hasil(self):
        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'hasil_uji'))
        fileNames = []
        for filename in os.listdir(path):
            fileNames.append(filename)
        
        fileNames.sort(key=lambda f: int(re.sub('\D', '', f)))
        
        texts = []

        for r, d, files in os.walk(path):
            for f in fileNames:
                text = open(os.path.join(r, f), 'r', encoding="utf-8-sig").read()
                texts.append(text)
        return texts

    def split_sentence(self, text):
        result = []
        for t in text:
            temp_result = []
            sentences = sent_tokenize(t)
            for sentence in sentences:
                if(re.compile('!important').search(sentence)):
                    if(re.compile('Baca juga:').search(sentence)):
                        sentences.remove(sentence)
                    else:
                        sentence = sentence.replace('(adsbygoogle = window.adsbygoogle || []).push({});', '')
                        temp_result.append(sentence.strip())
                else:
                    sentence = sentence.replace('(adsbygoogle = window.adsbygoogle || []).push({});', '')
                    temp_result.append(sentence.strip())
            result.append(temp_result)
        return result

    '''
    text: []
    '''
    def preprocessing(self, text):
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        result = []
        for t in text:
            # to lower case
            term = t.lower()
            stemmer.stem(t)
            # remove symbol
            term = term.translate(str.maketrans("","",string.punctuation))
            # remove whitespace
            term = term.strip()
            # tokenizing
            term = term.split()
            # remove unececary css/js string
            term_resul = []
            for tm in term:
                if((len(tm)) < 28 and tm != 'adsbygoogle' and tm != 'windowadsbygoogle'):
                    tm = (tm.encode('ascii', 'ignore')).decode("utf-8-sig")
                    if(tm != ''):
                        term_resul.append(tm)
            term = term_resul
            result.append(term)
        
        return result

    # def preprocessing_basic(self, text):
    #     factory = StemmerFactory()
    #     stemmer = factory.create_stemmer()
    #     term = text.lower()
    #     stemmer.stem(text)
    #     # remove symbol
    #     term = term.translate(str.maketrans("","",string.punctuation))
    #     # remove whitespace
    #     term = term.strip()
    #     # tokenizing
    #     term = term.split()
    #     return term