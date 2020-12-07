import json
from semantictagging.miner.abbr_base import AbbrBase
import pickle
import collections


if __name__ == '__main__':
    file_path = 'output/abbr_pair_result_sorted_12_03.pickle'
    save_path = 'output/abbr_pair_result_sorted_12_03.txt'
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    with open(save_path, 'w+') as f:
        for i in data:
            f.write('{} - {}\n'.format(i[0], i[1]))

