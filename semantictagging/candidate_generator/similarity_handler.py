#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pathlib import Path
import pickle

import numpy
from gensim.models import KeyedVectors
import textdistance

class SimilarityHandler:
    def __init__(self, wv=None, verbs=None, stopwords=None):
        self.wv = wv
        self.verbs = verbs
        self.DLDis = textdistance.DamerauLevenshtein()
        self.stopwords = set(stopwords) if stopwords is not None else set()
        if self.verbs is not None and self.wv is not None:
            invalid_verbs = set()
            for verb in verbs:
                if verb not in self.wv:
                    invalid_verbs.add(verb)
            self.verbs -= invalid_verbs
            self.verb_matrix = numpy.array([self.wv[verb] for verb in self.verbs])
            self.verb_matrix_norm = numpy.array([numpy.sqrt(numpy.dot(row, row)) for row in self.verb_matrix])

    def load_wv(self, path):
        wv = KeyedVectors.load(path)
        self.wv = wv

    def load_verbs(self, path):
        with Path(path).open("rb") as f:
            verbs = pickle.load(f)
        self.verbs = verbs
        if self.verbs is not None and self.wv is not None:
            invalid_verbs = set()
            for verb in verbs:
                if verb not in self.wv:
                    invalid_verbs.add(verb)
            self.verbs -= invalid_verbs
            self.verb_matrix = numpy.array([self.wv[verb] for verb in self.verbs if verb in self.wv])
            self.verb_matrix_norm = numpy.array([numpy.sqrt(numpy.dot(row, row)) for row in self.verb_matrix])

    def zero(self):
        return numpy.array([0.] * self.wv.vector_size)

    def center(self, phrases):
        vectors = [self.vector(phrase) for phrase in phrases]
        vectors = [vector for vector in vectors if vector is not None]
        if len(vectors) == 0:
            return None
        centric_vector = numpy.mean(vectors, 0)
        return centric_vector

    def select_centric_phrase(self, phrases):
        vectors = [self.vector(phrase) for phrase in phrases]
        vectors = [vector for vector in vectors if vector is not None]
        if len(vectors) == 0:
            return None
        center = numpy.mean(vectors, 0)
        sims = [(phrase, self.similarity_of_vectors(center, vector)) for phrase, vector in zip(phrases, vectors)]
        centric_phrase, _ = max(sims, key=lambda item:item[1])
        return centric_phrase

    def select_related_verbs(self, phrases, topK=None):
        center = self.center(phrases)
        if center is None:
            return []
        c_norm = numpy.sqrt(numpy.dot(center, center))
        # print(self.verb_matrix.shape)
        sims = numpy.dot(self.verb_matrix, center) / (self.verb_matrix_norm * c_norm)
        # sims = center * self.verb_matrix.T
        # print(sims.shape)
        # sims = sims.reshape([-1])
        # sims = [(verb, self.similarity_of_vectors(center, self.wv[verb])) for verb in self.verbs]
        sorted_verbs = list(sorted(zip(self.verbs, sims), key=lambda item: item[1], reverse=True))
        if topK:
            return sorted_verbs[:topK]
        return sorted_verbs

    def select_related_verbs_bad(self, phrases, topK=None):
        center = self.center(phrases)
        if center is None:
            return []
        sims = [(verb, self.similarity_of_vectors(center, self.wv[verb])) for verb in self.verbs]
        sorted_verbs = list(sorted(sims, key=lambda item: item[1], reverse=True))
        if topK:
            return sorted_verbs[:topK]
        return sorted_verbs

    def verbalize(self, word, dl_alpha=0.5, topK=50, candidate_num=None):
        word = word.lower()
        candidate_verbs = self.select_related_verbs([word], candidate_num)
        if len(candidate_verbs) == 0:
            return []
        verbs_with_score = []
        for verb, sim in candidate_verbs:
            score = (1 - dl_alpha) * sim + dl_alpha * self.DLDis.normalized_similarity(word, verb)
            verbs_with_score.append((verb, score))
        verbs_with_score = list(sorted(verbs_with_score, key=lambda item: item[1], reverse=True))
        if topK:
            return verbs_with_score[:topK]
        return verbs_with_score

    def vector(self, phrase):
        words = phrase.split()
        wvs = [self.wv[word] for word in words if word in self.wv and word not in self.stopwords]
        if len(wvs) == 0:
            return None
        return numpy.mean(wvs, 0)

    def similarity(self, phrase1, phrase2):
        vector1 = self.vector(phrase1)
        vector2 = self.vector(phrase2)
        if vector1 is None or vector2 is None:
            return 0
        # print(vector2)
        return self.similarity_of_vectors(vector1, vector2)

    def similarity_of_vectors(self, vector1, vector2):
        if vector1 is None or vector2 is None:
            return 0
        norm1 = numpy.sqrt(numpy.dot(vector1, vector1))
        norm2 = numpy.sqrt(numpy.dot(vector2, vector2))

        if norm1 == 0 or norm2 == 0:
            return 0
        cosine = numpy.dot(vector1, vector2) / (norm1 * norm2)
        score = 0.5 + 0.5 * cosine
        return score


