'''
Created on 2024/07/06

@author: kuyamakazuhiro
'''

import re
# from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.charfilter import RegexReplaceCharFilter
from janome.tokenfilter import CompoundNounFilter, POSKeepFilter


class WordRecomender:
    
    def __init__(self, cat):
        self.recomendations = None
        self.category = cat
        
    def createRecomendations(self):
        #選択されたイベント文字列から、キーワード候補となる文字列を抽出する。
        #イベント文字列の中で２回以上出現し、キーワード登録されていないものが候補
        token_filters = [CompoundNounFilter(),POSKeepFilter(['名詞'])]
        char_filters = [RegexReplaceCharFilter("\]|\[|\(|\)"," ")]
        a = Analyzer(char_filters=char_filters, token_filters=token_filters)       
        words = dict()
        for e in self.category['activities']:
            for token in a.analyze(f"{e['app']} {e['title']}"):
                word_str = token.surface
                if len(word_str) <= 1:
                    break
                if word_str in words:
                    words[token.surface] += 1
                else:
                    words[token.surface] = 1
        imlist = sorted(words.items(), key=lambda x:x[1], reverse=True)
#        print(f"imlist : {imlist}")
        filtered_list = self._deliminateUsedWords(imlist)
#        print(f"filterd_list : {filtered_list}")
        top_list = [x for x in filtered_list if x[1]>0]
        self.recomendations =self._addEventInformation(top_list) 
        
    def _deliminateUsedWords(self, wlist):
        #すでにキーワードとして登録されているものを外す
        defined_word_data = self.category['key_words']
        used_word_list = [x['word'] for x in defined_word_data]
        filtered_list = [item for item in wlist if item[0] not in used_word_list]
        #("ワード",出現数)を要素とするリストを返す
        return filtered_list
        
    def _addEventInformation(self, wlist):
        #キーワードが含まれる、イベントの情報を付加する
        wd_info_list = []
        for w in wlist:
            wd_dict = dict()
            evlist = []
            for ev in self.category['activities']:
                if re.search(w[0],f"{ev['app']} {ev['title']}"):
                    evlist.append([ev['app'],ev['title']])
            wd_dict['word']=w[0]
            wd_dict['count']=w[1]
            wd_dict['activity_list']= evlist
            wd_info_list.append(wd_dict)
        return wd_info_list

        