#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import pickle
import json
import os


class AbbrBase:
    # key is tuple: (abbr, full)
    # value is int value: count
    def __init__(self):
        self.base = dict()

    def add_pair(self, abbr, full, count=1):
        abbr_pair: tuple = (abbr, full)
        self.base[abbr_pair] = self.base.get(abbr_pair, 0) + count

    def get_full(self, abbr) -> list:
        result = list()
        for key in self.base.keys():
            if key[0] is abbr:
                result.append(key[1])
        return result

    def get_count(self, abbr, full) -> int:
        return self.base.get((abbr, full), 0)

    def save_to_file(self, file_path):
        print('start save data to file: %s' % file_path)
        if not os.path.exists(file_path):
            os.system(r"touch {}".format(file_path))
        with open(file_path, 'wb') as f:
            pickle.dump(self.base, f)
        print('successfully save data to file: %s' % file_path)

    def pretty_print(self):
        for i in self.base.keys():
            print('{} - {}'.format(i, self.get_count(i[0], i[1])))







