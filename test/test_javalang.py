#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pathlib import Path
from javalang.parse import parse
from javalang.tokenizer import Identifier
import sys

if __name__ == "__main__":
    with Path("../samples/sample1.java").open("r", encoding="utf-8") as f:
        code = f.read()

    # code = "class Foo {%s}" % code
    cu = parse(code)
    for _, node in cu:
        print(type(node).__name__, node.begin_token, "|", node.end_token)
        tokens_list = list()
        for token in node.tokens():
            if isinstance(token, Identifier):
                tokens_list.append(token.value)
        print(tokens_list)
        print('*'*50)
