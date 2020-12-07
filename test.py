#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pathlib import Path
import re
import json

from javalang.parse import parse
from javalang.tokenizer import Identifier, tokenize

from semantictagging.code_utils.cleaner import Cleaner
from semantictagging.code_utils.delimiter import Delimiter
from semantictagging.miner.abbr_miner import AbbrMiner
from semantictagging.candidate_generator.wiki_searcher import WikiSearcher

if __name__ == "__main__":
    # for py in Path("sourcererCC").rglob("*.py"):
    #     try:
    #         with Path(py).open("r", encoding="utf-8") as f:
    #             code = f.read()
    #         code = re.sub(r"print (.*?)\n", r"print(\1)\n", code)
    #         with Path(py).open("w", encoding="utf-8") as f:
    #             f.write(code)
    #     except:
    #         pass
    # with Path("samples/ChainSyntaxTest.java").open("r", encoding="utf-8") as f:
    #     code = f.read()
    # AbbrMiner().mine(code)
    # tokens = tokenize(code)
    # tokens = Cleaner.clean_annotation(list(tokens))
    # for token in tokens:
    #     if isinstance(token, Identifier):
    #         print(token)
    #         print(Delimiter.split_camel(token.value))
    # generator = HashGenerator()
    # ast = parse(code)
    # for _, mi in ast.filter(MethodInvocation):
    #     print(generator.generate_fingerprint(mi))

    # alias_table = {}
    # alias_table["add"] = {
    #     1: set(["add"]),
    #     2: set(["add word", "add item"]),
    #     3: set(["add a b"])
    # }
    # alias_table["remove"] = {
    #     1: set(["remove"]),
    #     2: set(["remove word", "remove item"]),
    #     3: set(["remove a b"])
    # }

    # sent = ["afd", "fd", "add", "word", "remove", "cccc"]

    # index = 0
    # result = []
    # while index < len(sent):
    #     word = sent[index]
    #     if word not in alias_table:
    #         index += 1
    #         continue
    #     for length, alias_set in sorted(alias_table[word].items(), key=lambda item: item[0], reverse=True):
    #         condidate = " ".join(sent[index: index+length])
    #         if condidate in alias_set:
    #             result.append(condidate)
    #             index += length
    #             break
    #     else:
    #         index += 1
    # print(result)

    wiki_searcher = WikiSearcher(api="https://en.jinzhao.wiki/w/api.php")
    title2entries = wiki_searcher.search_entries(["lum"])
    print(json.dumps(title2entries, indent=4))
    title2page = wiki_searcher.fetch_page([1827236])
    print(json.dumps(title2page, indent=4))
