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

        with open(self.file_in, encoding="utf-8") as input_file:
            with open(self.file_out, mode="w", encoding="utf-8") as output_file:
                initial_parsed = MeCab.Tagger("-Ochasen").parse(input_file.read())
                output_file.write(initial_parsed)

        self.raw_table = pd.read_table(self.file_out, header=None)
        os.remove(self.file_out)

        self.file_dir, self.file_name_with_extension = os.path.split(file_in)
        self.file_name, self.extension = os.path.splitext(self.file_name_with_extension)


    def initial_parse(self):

        self.raw_table.to_csv(os.path.join(self.file_dir, self.file_name+"_initial.csv"))
        return self.raw_table


    def clean_parse(self, kanji="only", remove_pos = ["助詞", "記号"], sort_by=["単語", "フリガナ", "品詞"]):

        #Take Columns 0, 1, and 3, which are the words, pronunciations, and POS respectively.
        new_sorted_data = self.raw_table[[0, 1, 3]].drop_duplicates()
        new_sorted_data.columns = ["単語", "フリガナ", "品詞"]
        
        #Remove unwanted POS
        remove_pos = "|".join(remove_pos)
        pos_filter = new_sorted_data["品詞"].str.contains(remove_pos)
        pos_filter = ~pos_filter.fillna(False)
        word_table = new_sorted_data[pos_filter]

        #Remove non-kanji words
        if kanji == "only":
            kanji_pattern = re.compile(r'^[\u4E00-\u9FD0]+$')
            kanji_filter = word_table["単語"].str.contains(kanji_pattern, regex=True)

        elif kanji == "mixed":
            kanji_pattern = re.compile(r'[\u4E00-\u9FD0]')
            kanji_filter = word_table["単語"].apply(lambda x : kanji_pattern.search(x) != None)

        elif kanji == "none":
            kanji_pattern = re.compile(r'[\u4E00-\u9FD0]')
            kanji_filter = word_table["単語"].apply(lambda x : kanji_pattern.search(x) == None)

        word_table = word_table[kanji_filter]

        
        #Sort and Drop Duplicates
        word_table = word_table.sort_values(by=sort_by)
        word_table.index = np.arange(word_table.shape[0])
        word_table.style.set_properties(**{'text-align': 'right'})
        self.word_table = word_table

        self.word_table.to_csv(os.path.join(self.file_dir, self.file_name + "_clean.csv"))
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
    

