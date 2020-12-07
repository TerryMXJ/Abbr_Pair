#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import itertools
from pathlib import Path

from semantictagging.utils.pair_checker import PairChecker
from javalang.tokenizer import Identifier, tokenize
from semantictagging.utils.code_cleaner import CodeCleaner
from semantictagging.utils.delimiter import Delimiter
from semantictagging.utils.code_pos import CodePOS


if __name__ == "__main__":
    with Path("samples/Foo.java").open("r", encoding="utf-8") as f:
        code = f.read()
    code_pos = CodePOS.get_inst()
    pair_checker = PairChecker.get_inst()
    tokens = tokenize(code)
    tokens = CodeCleaner.clean_annotation(list(tokens))
    identifiers = list()
    for token in tokens:
        if isinstance(token, Identifier):
            identifiers.append(Delimiter.split_camel(token.value))
    for identifier in identifiers:
        print(code_pos(identifier))
    # print(identifiers)