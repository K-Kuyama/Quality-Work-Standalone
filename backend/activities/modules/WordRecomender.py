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
        
    def createRecomendations(self, limitation=50):
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
        #count数が2以上のもののみリストに残す
        top_list = [x for x in filtered_list if x[1]>1]
        #さらに最大個数までのリストに整形
        eliminated_top_list = top_list[:limitation]
        self.recomendations =self._listToDict(eliminated_top_list) 
        
    def _deliminateUsedWords(self, wlist):
        #すでにキーワードとして登録されているものを外す
        defined_word_data = self.category['key_words']
        used_word_list = [x['word'] for x in defined_word_data]
        filtered_list = [item for item in wlist if item[0] not in used_word_list]
        #("ワード",出現数)を要素とするリストを返す
        return filtered_list
        
    def _listToDict(self, wlist):
        #辞書型に変換
        wd_info_list = []
        for w in wlist:
            wd_dict = dict()
            wd_dict['word']=w[0]
            wd_dict['count']=w[1]
            wd_info_list.append(wd_dict)
        return wd_info_list

        