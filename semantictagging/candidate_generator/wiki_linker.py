#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import re
import pickle
from pathlib import Path

from gensim.models import KeyedVectors
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy
from bs4 import BeautifulSoup
from tqdm import tqdm

from definitions import EMB_DIR
from .pipe import Pipe
from ..common.wiki_searcher import WikiSearcher
from ..common.similarity_handler import SimilarityHandler
from ..types import Clazz


class WikiLinker(Pipe):
    def __init__(self, wiki_searcher: WikiSearcher = None, similarity_handler=None):
        super(WikiLinker, self).__init__()
        self.wiki_searcher = wiki_searcher
        if not self.wiki_searcher:
            self.wiki_searcher = WikiSearcher(host=self.opt.wiki_host, proxy=self.opt.proxy)
        self.similarity_handler = similarity_handler
        if not self.similarity_handler:
            wv = KeyedVectors.load_word2vec_format(str(Path(EMB_DIR) / "glove.6B.100d.txt"))
            self.similarity_handler = SimilarityHandler(wv=wv, stopwords=set(stopwords.words('english')))

    # def compute_similarity(self, phrase1, phrase2):
    #     words1 = [word for word in word_tokenize(phrase1.lower()) if word not in self.STOPWORDS]
    #     words2 = [word for word in word_tokenize(phrase2.lower()) if word not in self.STOPWORDS]
    #     if len(words1) == 0 or len(words2) == 0:
    #         return 0

    #     vector1 = numpy.mean([self.w2v[word] if word in self.w2v else 0 for word in words1], 0)
    #     vector2 = numpy.mean([self.w2v[word] if word in self.w2v else 0 for word in words2], 0)
    #     norm1 = numpy.sqrt(numpy.dot(vector1, vector1))
    #     norm2 = numpy.sqrt(numpy.dot(vector2, vector2))

    #     if norm1 == 0 or norm2 == 0:
    #         return 0
    #     cosine = numpy.dot(vector1, vector2) / (norm1 * norm2)
    #     score = 0.5 + 0.5 * cosine
    #     return score

    def select_def_for_type_name_pair(self, type_defs, name_defs, ratio=0.5, threashold=0.6):
        type_title_vectors = []
        type_def_vectors = []
        for type_title, type_def in type_defs:
            title_vec = self.similarity_handler.vector(" ".join(word_tokenize(type_title.lower())))
            type_title_vectors.append(title_vec if title_vec is not None else self.similarity_handler.zero())
            def_vec = self.similarity_handler.vector(" ".join(word_tokenize(type_def.lower())))
            type_def_vectors.append(def_vec if def_vec is not None else self.similarity_handler.zero())
        type_title_matrix = numpy.array(type_title_vectors)
        type_title_matrix_norm = numpy.array([[numpy.sqrt(numpy.dot(vector, vector))] for vector in type_title_vectors])

        # text_sims = numpy.dot(type_title_matrix, type_vec)
        # text_sims = text_sims / (type_title_matrix_norm * type_vec_norm)

        type_def_matrix = numpy.array(type_def_vectors)
        type_def_matrix_norm = numpy.array([[numpy.sqrt(numpy.dot(vector, vector))] for vector in type_def_vectors])

        # print(type_title_matrix.shape)

        name_title_vectors = []
        name_def_vectors = []
        for name_title, name_def in name_defs:
            title_vec = self.similarity_handler.vector(" ".join(word_tokenize(name_title.lower())))
            # if name_title == "Index (A Certain Magical Index)":
            # print(title_vec)
            # print(title_vec if title_vec is not None else 0)
            name_title_vectors.append(title_vec if title_vec is not None else self.similarity_handler.zero())
            def_vec = self.similarity_handler.vector(" ".join(word_tokenize(name_def.lower())))
            name_def_vectors.append(def_vec if def_vec is not None else self.similarity_handler.zero())
        # print(name_title_vectors)
        name_title_matrix = numpy.array(name_title_vectors)
        name_title_matrix_norm = numpy.array([[numpy.sqrt(numpy.dot(vector, vector))] for vector in name_title_vectors])
        # print(name_title_matrix)
        # print(name_title_matrix.shape)
        name_def_matrix = numpy.array(name_def_vectors)
        name_def_matrix_norm = numpy.array([[numpy.sqrt(numpy.dot(vector, vector))] for vector in name_def_vectors])

        title_norm = numpy.dot(type_title_matrix_norm, name_title_matrix_norm.T)
        title_norm = numpy.where(title_norm != 0, title_norm, 1)
        title_sim_matrix = numpy.dot(type_title_matrix, name_title_matrix.T) / title_norm
        def_norm = numpy.dot(type_def_matrix_norm, name_def_matrix_norm.T)
        def_norm = numpy.where(def_norm != 0, def_norm, 1)
        def_sim_matrix = numpy.dot(type_def_matrix, name_def_matrix.T) / def_norm

        # mask for threshold
        title_mask = numpy.where(title_sim_matrix >= threashold, 1, 0)
        def_mask = numpy.where(def_sim_matrix >= threashold, 1, 0)
        # print(title_sim_matrix)
        # print(title_sim_matrix)
        # print(def_sim_matrix)
        sim_matrix = ratio * title_sim_matrix + (1 - ratio) * def_sim_matrix
        sim_matrix = sim_matrix * title_mask * def_mask
        # print(sim_matrix)

        x, y = numpy.unravel_index(numpy.argmax(sim_matrix), sim_matrix.shape)
        # print(x, y)
        # print(title_sim_matrix[x, y])
        # print(def_sim_matrix[x, y])
        # print(sim_matrix[x, y])
        similarity = sim_matrix[x, y]
        return type_defs[x][0], type_defs[x][1], name_defs[y][0], name_defs[y][1], similarity

    def load_wiki_cache(self):
        if self.opt.wiki_cache_path:
            cache_path = Path(self.opt.wiki_cache_path)
            if cache_path.exists():
                with cache_path.open("rb") as f:
                    return pickle.load(f)
        return {}

    def save_wiki_cache(self, wiki_cache):
        if self.opt.wiki_cache_path:
            with Path(self.opt.wiki_cache_path).open("wb") as f:
                pickle.dump(wiki_cache, f)

    def link(self, clazz: Clazz, text2defs=None, ratio=0.5, threashold=0.6):
        fields = clazz.inherited_fields + clazz.fields
        methods = clazz.inherited_methods + clazz.methods
        if text2defs is None:
            text2defs = dict()

        entity2type = dict()
        texts = set()

        name2type = dict()
        for field in fields:
            _type, name = field.delimited_type, field.selected_name
            if _type == name:
                continue
            if _type in Clazz.PRIME_TYPES:
                continue
            if name not in name2type:
                name2type[name] = _type
            elif len(_type.split()) > len(name2type[name].split()):
                name2type[name] = _type
            type_entity = field.type_entity
            for entity in type_entity:
                texts.add(entity.name)
                for alias in entity.aliases:
                    if len(alias) == 1:
                        continue
                    if alias in name2type:
                        entity2type[entity] = name2type[alias]
                        texts.add(name2type[alias])
                        break
        for method in methods:
            for (_type, _), name in zip(method.delimited_params, method.selected_params):
                if _type == name:
                    continue
                if _type in Clazz.PRIME_TYPES:
                    continue
                if name not in name2type:
                    name2type[name] = _type
                elif len(_type.split()) > len(name2type[name].split()):
                    name2type[name] = _type
            for entity in method.local_entities:
                texts.add(entity.name)
                for alias in entity.aliases:
                    if len(alias) == 1:
                        continue
                    if alias in name2type:
                        entity2type[entity] = name2type[alias]
                        texts.add(name2type[alias])
                        break

        for entity in clazz.entities:
            texts.add(entity.name)
            for alias in entity.aliases:
                if len(alias) == 1:
                    continue
                if alias in name2type:
                    entity2type[entity] = name2type[alias]
                    texts.add(name2type[alias])
                    break

        # print(texts)
        _text2defs_with_score = self.wiki_searcher.search_definitions(texts, name2type, self.similarity_handler,
                                                                      page_limit=25,
                                                                      sent_limit=1, threashold=threashold)
        _text2defs = dict()
        for k in _text2defs_with_score:
            _text2defs[k] = _text2defs_with_score[k]
        text2defs.update(_text2defs)
        # print(text2defs)

        entities_in_wiki = set()
        entities_with_type = set()
        for entity in clazz.entities:
            if entity.name in text2defs:
                entities_in_wiki.add(entity)
            if entity in entity2type and entity2type[entity] in text2defs:
                entities_with_type.add(entity)

        handled_entities = set()
        for entity in entities_with_type:
            # print("entity:", entity.name) 
            name = entity.name
            _type = entity2type[entity]
            # print(f"name: {name}, type: {_type}")

            name_defs = text2defs[name]
            type_defs = text2defs[_type]
            entity.definition = name_defs
            entity.wiki_title = type_defs
            handled_entities.add(entity)
            # type_title, type_def, name_title, name_def, sim = self.select_def_for_type_name_pair(type_defs, name_defs,
            #                                                                                      ratio, threashold)
            # if sim >= threashold:
            #     entity.definition = name_def
            #     entity.wiki_title = name_title
            #     handled_entities.add(entity)
        for entity in entities_in_wiki:
            name = entity.name
            name_defs = text2defs[name]
            entity.definition = name_defs
        return entities_in_wiki, entities_with_type

    def process(self, clazzes):
        text2defs = self.load_wiki_cache()
        print(f"total clazz num: {len(clazzes)}")
        for clazz in tqdm(clazzes, desc=' - (Wiki Linker)', leave=False, ascii=True):
            self.link(clazz, text2defs)
        self.save_wiki_cache(text2defs)
        return clazzes
