#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import re

from bs4 import BeautifulSoup
from bs4.element import Tag

class WikiPage:
    def __init__(self, title, pageid, redirects, text, categories):
        self.title = title
        self.pageid = pageid
        self.redirects = redirects
        self.text = text
        self.categories = categories
        self.abstract = None
        self.disambiguation_groups = None

    def is_disambiguation(self):
        for cat in self.categories:
            if "category" in cat and str(cat["category"]).lower().find("disambiguation") >= 0:
                return True
        return False

    def get_abstract(self):
        if self.abstract is not None:
            return self.abstract
        
        self.abstract = ""
        if self.is_disambiguation():
            return self.abstract
        
        soup = BeautifulSoup(self.text, "lxml")
        if soup is None:
            return self.abstract
        content = soup.find(class_="mw-parser-output")
        if content is None:
            return self.abstract
        
        paragraphs = list()
        for ele in content.children:
            if type(ele) != Tag:
                continue
            if ele.has_attr("role") and ele["role"] == "navigation":
                break
            if ele.name == "p":
                paragraph = ele.get_text()
                paragraph = re.sub(r"\[[0-9]+\]|\{\\displaystyle .*?\}", "", paragraph)
                paragraph = re.sub(r"\s+", " ", paragraph).strip()
                paragraphs.append(paragraph)
        # print(paragraphs)
        # for paragraph in content.find_all("p"):
        #     paragraph = paragraph.get_text().strip()
        #     paragraph = re.sub(r"\[[0-9]+\]|\{\\displaystyle .*?\}", "", paragraph)
        #     paragraph = re.sub(r"\s+", " ", paragraph)
        #     print(paragraph)
        self.abstract = "\n".join(paragraphs)
        return self.abstract

    def get_disambiguation_groups(self):
        if self.disambiguation_groups is not None:
            return self.disambiguation_groups
        
        self.disambiguation_groups = dict()
        if not self.is_disambiguation():
            return self.disambiguation_groups
        
        soup = BeautifulSoup(self.text, "lxml")
        if soup is None:
            return self.disambiguation_groups
        content = soup.find(class_="mw-parser-output")
        if content is None:
            return self.disambiguation_groups
        group_title = "*"
        for ele in content.children:
            if type(ele) != Tag:
                continue
            if ele.name == "h2":
                span = content.find("span", {"class": "mw-headline"})
                group_title = span.get_text() if span is not None else None
            elif ele.name == "ul":
                group = []
                for li in ele.findAll("li"):
                    if li.a is None or "title" not in li.a.attrs:
                        continue
                    if not li.a["href"].startswith("/wiki") or li.a["title"].startswith("Special:"):
                        continue
                    group.append({
                        "title": li.a["title"],
                        "description": li.get_text()})
                if len(group) == 0:
                    group_title = "*"
                    continue
                if group_title in self.disambiguation_groups:
                    self.disambiguation_groups[group_title].extend(group)
                else:
                    self.disambiguation_groups[group_title] = group
                group_title = "*"
        return self.disambiguation_groups
        

    def to_json(self):
        return {
            "title": self.title,
            "pageid": self.pageid,
            "redirects": self.redirects,
            "text": self.text,
            "categories": self.categories
        }

    def __repr__(self):
        return json.dumps(self.to_json(), indent=4)

    def __str__(self):
        return json.dumps(self.to_json(), indent=4)