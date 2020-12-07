#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
from semantictagging.candidate_generator.wiki_parser import WikiParser
from semantictagging.candidate_generator.wiki_searcher import WikiSearcher

if __name__ == "__main__":
    wiki_searcher = WikiSearcher(api="https://en.jinzhao.wiki/w/api.php")
    wiki_parser = WikiParser()
    # title2entries = wiki_searcher.search_entries(["Luminescence"])
    # print(title2entries)
    title2page = wiki_searcher.fetch_page(["Luminance (disambiguation)"])
    # print(title2page)
    for _, page in title2page.items():
        print(page.text)
        abstract = page.get_abstract()
        print(abstract)
        disambiguations = page.get_disambiguation_groups()
        print(disambiguations)
