#!/usr/bin/env python
# coding: utf-8

import sys
import os
import re
import numpy as np
import pandas as pd
import MeCab

class MecabParser:

    def __init__(self, file_in):
        self.file_in = file_in
        self.file_out = self.file_in + ".mecab"

        # tagger = MeCab.Tagger("-Ochasen")
        tagger = MeCab.Tagger()
        with open(self.file_in, encoding="utf-8") as input_file:
            with open(self.file_out, mode="w", encoding="utf-8") as output_file:
                initial_parsed = tagger.parse(input_file.read())
                output_file.write(initial_parsed)

        self.raw_table = pd.read_table(self.file_out, header=None)
        os.remove(self.file_out)

        self.file_dir, self.file_name_with_extension = os.path.split(file_in)
        self.file_name, self.extension = os.path.splitext(self.file_name_with_extension)

        #Build dictionary that helps convert katagana to hiragana
        str_hira = "あいうえおぁぃぅぇぉかきくけこがぎぐげごさしすせそざじずぜぞたちつてとっだぢづでどなにぬねのはひふへほばびぶべぼぱぴぷぺぽまみむめもやゆよゃゅょらりるれろわをん"
        str_kata = "アイウエオァィゥェォカキクケコガギグゲゴサシスセソザジズゼゾタチツテトッダヂヅデドナニヌネノハヒフヘホバビブベボパピプペポマミムメモヤユヨャュョラリルレロワヲン"
        list_hira = list(str_hira)
        list_kata = list(str_kata)
        self.dic_kata_to_hira = dict(zip(list_kata, list_hira))

    def kata_to_hira(self, word):

        new_word = list(word)
        for i in range(len(word)):
            new_word[i] = self.dic_kata_to_hira.get(new_word[i], new_word[i])
        new_word = "".join(new_word)

        return new_word

    def initial_parse(self):

        #Save initial parsed results to csv
        self.raw_table.to_csv(os.path.join(self.file_dir, self.file_name+"_initial.csv"), encoding="utf-8-sig")

        return self.raw_table


    def clean_parse(self, kanji="only", remove_pos = ["助詞", "記号"], sort_by=["単語", "振り仮名", "品詞"], hiragana_to_furigana=True):

        """
        kanji: Specify if you want items that contain "only" kanji, is "mixed" with kanji, or consists of "none" kanji characters.
        remove_pos: Specify unwanted parts of speech--such as "助詞", "記号" as they mean little.
        sort_by: Specify how you want the table to be sorted.
        hiragana_to_furigana: Set it to True if you want to convert the hiragana readings to furigana ones.
        """

        #Take Columns that show words, pronunciations, and POS respectively.
        new_sorted_data = self.raw_table[[0, 2, 4]].drop_duplicates()
        new_sorted_data.columns = ["単語", "振り仮名", "品詞"]

        #Convert katakana to hiragana
        if hiragana_to_furigana:
            new_sorted_data["振り仮名"] = new_sorted_data["振り仮名"].astype(str).apply(self.kata_to_hira)

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

        #Save clean parsed results to csv
        self.word_table.to_csv(os.path.join(self.file_dir, self.file_name + "_clean.csv"), encoding="utf-8-sig")

        return self.word_table

# Output clean parsed results of a file in command line
# Command: python path/to/MecabParserModule.py path/to/file
if __name__ == "__main__":
    input_file = sys.argv[1]
    parser = MecabParser(input_file)
    print(parser.clean_parse())