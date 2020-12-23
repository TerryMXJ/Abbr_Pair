#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import textdistance
import itertools
import functools
import numpy as np

from .lemmatizer import Lemmatizer

class PairChecker:
    __INSTANCE = None

    def __init__(self):
        self.DLDis = textdistance.DamerauLevenshtein()

    @functools.lru_cache(maxsize=10000)
    def normalize(self, term):
        lemma = Lemmatizer.lemmatize_noun(term)
        name = lemma.replace("-", " ")
        name = re.sub(r"\s+", " ", name)
        return name

    def check_synonym(self, long_term, short_term, max_dis=2, threshold=0.25):
        if long_term.isupper() and short_term.isupper():
            return False
        # if long_term.lower().rstrip("s") == short_term.lower().rstrip("s"):
        #     return True

        long_name = self.normalize(long_term)
        short_name = self.normalize(short_term)

        if long_name == short_name:
            return True
        if long_name.replace(" ", "") == short_name.replace(" ", ""):
            return True

        long_words = long_name.split()
        short_words = short_name.split()

        if len(long_words) != len(short_words):
            return False
        for word1, word2 in zip(long_words, short_words):
            if word1[0] != word2[0]:
                return False
            if re.findall(r'[0-9]+', word1) != re.findall(r'[0-9]+', word2):
                return False
            if self.DLDis.distance(word1, word2) > max_dis or self.DLDis.normalized_distance(word1, word2) >= threshold:
                return False
        return True

    @staticmethod
    def __check_word_word(long_word, word):
        if PairChecker.__check_subseq(long_word, word):
            return True
        return False

    @staticmethod
    def __check_subseq(long_word, word):
        i = j = 0
        while i < len(long_word) and j < len(word):
            if long_word[i] == word[j]:
                j = j + 1
            i = i + 1
        return j == len(word)

    @staticmethod
    def __check_phrase_word(phrase, word):
        print('get into check_phrase_word method...')
        words = phrase.split()
        if len(word) < len(words):
            return False
        if len(words) == 1:
            return PairChecker.__check_word_word(phrase, word)
        else:
            for indices in itertools.combinations([i for i in range(1, len(word), 1)], len(words) - 1):
                print(indices)
                copied_words = words.copy()
                indices = (0, ) + indices + (len(word), )
                # print(indices)
                pairs = [(beg, end) for (beg, end) in zip(indices[:-1], indices[1:])]
                beg, end = pairs.pop(0)
                cur_chars = word[beg:end]
                
                cur_word = copied_words.pop(0)
                # print(cur_chars, cur_word)
                if cur_chars[0] == cur_word[0]:
                    if not PairChecker.__check_word_word(cur_word, cur_chars):
                        continue
                elif cur_word[0] in set("aeiou") and len(cur_word) > 1 and cur_chars[0] == cur_word[1]:
                    if end != 1:
                        continue
                else:
                    continue

                for (beg, end), cur_word in zip(pairs, copied_words):
                    cur_chars = word[beg:end]
                    # print(cur_chars, cur_word)
                    if not PairChecker.__check_word_word(cur_word, cur_chars):
                        break
                else:
                    return True

            return False

    def check_abbr(self, long_name, short_name, lemma=True):
        if lemma:
            long_name = self.normalize(long_name)
            short_name = self.normalize(short_name)

        # print(long_name, short_name)

        if len(short_name.split()) == 1:
            return PairChecker.__check_phrase_word(long_name, short_name)
        else:
            short_words = short_name.split()
            long_words = long_name.split()
            if len(long_words) < len(short_words):
                return False
            while len(short_words) > 0 and short_words[0] == long_words[0]:
                short_words.pop(0)
                long_words.pop(0)
            while len(short_words) > 0 and short_words[-1] == long_words[-1]:
                short_words.pop(-1)
                long_words.pop(-1)
            if len(short_words) == 1:
                # print(long_words, short_words)
                return PairChecker.__check_phrase_word(" ".join(long_words), short_words[0])
            elif len(short_words) == len(long_words):
                for word1, word2 in zip(long_words, short_words):
                    if not PairChecker.__check_word_word(word1, word2):
                        return False
                return True
            return False

    @classmethod
    def get_inst(cls):
        if not cls.__INSTANCE:
            cls.__INSTANCE = cls()
        return cls.__INSTANCE