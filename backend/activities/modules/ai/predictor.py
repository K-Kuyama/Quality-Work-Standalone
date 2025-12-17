'''
Created on 2025/08/21

@author: kuyamakazuhiro
'''

import os
import pickle
#import logging
#import MeCab
#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.metrics import classification_report
from activities.modules.ai.util import tokenize, evaluation_report

#logger = logging.getLogger('django')

class Predictor:

    def __init__(self, location, name, tokenizer):
        self.location = location
        self.name = name
        self.label_encoder = None
        self.vectorizer = None
        self.model = None
        self.tokenizer = tokenizer

        with open(os.path.join(self.location,'label.pickle'), 'rb') as veb:
            self.label_encoder = pickle.load(veb)
        with open(os.path.join(self.location,'vectorizer.pickle'), 'rb') as veb:
            self.vectorizer = pickle.load(veb)
        with open(os.path.join(self.location,'model.pickle'), 'rb') as reb:
            self.model = pickle.load(reb)
        #logger.info(f"initialize predictor {self}")

    def get_name(self):
        return self.name
    
    def predict(self, text):
        tokenized_texts = [tokenize(self.tokenizer, t) for t in [text]]
        X = self.vectorizer.transform(tokenized_texts)
        labels = self.model.predict(X)
        probas = self.model.predict_proba(X)
        result_labels = self.label_encoder.inverse_transform(labels)
        id = result_labels[0]
        if type(id) != 'int':  # Pandasを使わない場合、idはstr型で渡されてしまうので変換。
            id = int(id)
        #return result_labels[0], probas[0][labels[0]]
        return id, probas[0][labels[0]]
    
    def evaluate(self, encoded_text, encoded_label, names):
        y_pred = self.model.predict(encoded_text)
        report = evaluation_report(encoded_label, y_pred, names)
        return report