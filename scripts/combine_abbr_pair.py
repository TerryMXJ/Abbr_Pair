import pickle
import json
from semantictagging.miner.abbr_base import AbbrBase

if __name__ == '__main__':
    abbr_base = AbbrBase()
    result_path = 'output/abbr_pair_result_12_10.pickle'
    for i in range(1, 17):
        print('start process file: %s' % i)
        file_path = 'output/abbr_pair/abbr_pair_%d.pickle' % i
        with open(file_path, 'rb') as f:
            data: dict = pickle.load(f)
        for pair in data.keys():
            abbr = pair[0]
            full = pair[1]
            count = data[pair]
            abbr_base.add_pair(abbr=abbr, full=full, count=count)
    abbr_base.save_to_file(result_path)
