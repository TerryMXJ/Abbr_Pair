#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pymysql
import os
from multiprocessing import Pool
import pickle

from semantictagging.miner.abbr_miner import AbbrMiner


def fetch_codes():
    db = pymysql.connect(host="10.176.64.33",
                         user="root",
                         passwd="123456",
                         db="code_comprehension_db",
                         port=3306,
                         charset='utf8'
                         )
    cursor = db.cursor(pymysql.cursors.SSCursor)
    sql = "SELECT * FROM classeswithoutcomment"
    cursor.execute(sql)
    record = cursor.fetchone()
    while record is not None:
        # cid, class_content, pid = record
        yield record
        record = cursor.fetchone()
    cursor.close()
    db.close()


def mine_process(file_path, i):
    abbr_miner = AbbrMiner()
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    print('open file %s successfully...' % file_path)
    # match abbr pair
    abbr_base = abbr_miner.mine(data, i)
    # write result
    save_path = "output/abbr_pair/abbr_pair_%d.pickle" % i
    abbr_base.save_to_file(save_path)


if __name__ == "__main__":
    p = Pool(40)
    for i in range(1, 17):
        file_path = '/home/fdse/wangchong/SemanticTagging/input/classes-batch%d.pkl' % i
        p.apply_async(mine_process, args=(file_path, i, ))
    p.close()
    p.join()
    print('all subprocesses done...')





