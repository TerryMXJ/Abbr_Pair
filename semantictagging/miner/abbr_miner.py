#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import itertools

import sys

from javalang.tokenizer import Identifier, tokenize
from ..utils.pair_checker import PairChecker
from ..utils.code_cleaner import CodeCleaner
from ..utils.delimiter import Delimiter
from .abbr_base import AbbrBase

from javalang.parse import parse
from javalang.tree import VariableDeclaration, FieldDeclaration, MethodInvocation

# from nltk.corpus import words


# modify the default recursion limit set by python
sys.setrecursionlimit(10 ** 6)


class AbbrMiner:
    def __init__(self):
        self.pair_checker = PairChecker.get_inst()
        # self.english_vocab = set(w.lower() for w in words.words())

    def process_code(self, code):
        # select tokenize method
        identifiers = self.tokenize_code_based_on_ast(code)
        pairs = set()
        for term1, term2 in itertools.combinations(identifiers, 2):
            long_term, short_term = (term1, term2) if len(term1) >= len(term2) else (term2, term1)
            # filter the short_term which is a word
            # if self.pair_checker.check_abbr(short_term, long_term) and short_term in self.english_vocab:
            if self.pair_checker.check_abbr(short_term, long_term):
                pairs.add((short_term, long_term))
        return pairs

    def mine(self, codes, i) -> AbbrBase:
        abbr_base = AbbrBase()
        count = 0
        for code in codes:
            print('[%d]start process code %d...' % (i, count))
            count += 1
            try:
                pairs = self.process_code(code)
                for pair in pairs:
                    abbr_base.add_pair(abbr=pair[0], full=pair[1])
            except Exception:
                print('[%d]process code %d error' % (i, count))
        return abbr_base

    def tokenize_code(self, code) -> set:
        identifiers = set()
        tokens = tokenize(code)
        tokens = CodeCleaner.clean_annotation(list(tokens))
        for token in tokens:
            if isinstance(token, Identifier):
                for split_value in Delimiter.split_camel(token.value).split():
                    identifiers.add(split_value)
        return identifiers

    def tokenize_code_based_on_ast(self, code) -> set:
        identifiers = set()
        node_types = (VariableDeclaration, FieldDeclaration, MethodInvocation)
        cu = parse(code)
        for path, node in cu:
            if isinstance(node, node_types):
                for token in node.tokens():
                    if isinstance(token, Identifier):
                        for split_value in Delimiter.split_camel(token.value).split():
                            identifiers.add(split_value)
        return identifiers
