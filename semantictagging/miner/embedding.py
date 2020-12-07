#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class Embedding:
    def __init__(self):
        self.embedding = dict()

    def train(self, codes):
        pass

    def preprocess(self, code):
        return code

    def corpus_generator(self, codes):
        for code in codes:
            yield self.preprocess(code)