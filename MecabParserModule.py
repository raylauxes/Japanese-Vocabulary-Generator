#!/usr/bin/env python
# coding: utf-8

import MeCab
import pandas as pd
import numpy as np
import re
import os

class MecabParser:

    def __init__(self, file_in):
        self.file_in = file_in
        self.file_out = self.file_in + ".mecab"

    def initial_parser(self):
        file_in = self.file_in
        file_out = self.file_out
        tagger = MeCab.Tagger("-Ochasen")

        with open(file_in, encoding="utf-8") as input_file:
            with open(file_out, mode="w", encoding="utf-8") as output_file:
                parsed_result = tagger.parse(input_file.read())
                output_file.write(parsed_result)

        self.raw_table = pd.read_table(file_out, header=None)
        os.remove(file_out)

        return self.raw_table
    
    
    def clean_parser(self, kanji_only=True, remove_pos = ["助詞", "記号"]):
        #CREATE NEW TABLE #Only take Columns 0, 1, and 3 and name them.
        new_sorted_data = self.raw_table[[0, 1, 3]].copy()
        new_sorted_data.columns = ["単語", "フリガナ", "品詞"]
        
        #Remove unwanted POS
        remove_pos = "|".join(remove_pos)
        pos_filter = new_sorted_data["品詞"].str.contains(remove_pos)
        pos_filter = ~pos_filter.fillna(False)
        word_table = new_sorted_data[pos_filter]
        
        #Sort and Drop Duplicates
        word_table = word_table.sort_values(by = "単語")
        word_table = word_table.drop_duplicates() #DataFrame.drop_duplicates(self, subset=None, keep='first', inplace=False)[source]
        word_table.index = np.arange(word_table.shape[0])
        word_table.style.set_properties(**{'text-align': 'left'})
        self.word_table = word_table
        
        return self.word_table
    
    def hiragana_parser(self):
        hira_table = self.word_table[:]
        hira_table.insert(1, "ふりがな", hira_table[:].iloc[:, 1])

        row_count = len(hira_table)
        for i in range(row_count):
            pronunciation = hira_table.iloc[i, 1]
            hira_table.iloc[i, 1] = self.kata_to_hira(pronunciation)

        hira_table = hira_table.drop(["フリガナ"], axis=1)
        
        return hira_table
    
    
    def kata_to_hira(self, word):
        str_hira = "あいうえおぁぃぅぇぉかきくけこがぎぐげごさしすせそざじずぜぞたちつてとっだぢづでどなにぬねのはひふへほばびぶべぼぱぴぷぺぽまみむめもやゆよゃゅょらりるれろわをん"
        str_kata = "アイウエオァィゥェォカキクケコガギグゲゴサシスセソザジズゼゾタチツテトッダヂヅデドナニヌネノハヒフヘホバビブベボパピプペポマミムメモヤユヨャュョラリルレロワヲン"

        list_hira = []
        for i in str_hira:
            list_hira.append(i)

        list_kata = []
        for i in str_kata:
            list_kata.append(i)

        dic_kata_to_hira = {}
        for i in np.arange(len(list_kata)):
                dic_kata_to_hira.update({list_kata[i]:list_hira[i]})
        new_word = ""

        for index, char in enumerate(word):
            if char in dic_kata_to_hira.keys():
                new_word += dic_kata_to_hira[char]
            else:
                new_word += char

        return new_word
    

