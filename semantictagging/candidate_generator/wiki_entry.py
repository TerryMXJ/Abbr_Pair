#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json

class WikiEntry:
    def __init__(self, namespace, title, pageid, snippet, section):
        self.namespace = namespace
        self.title = title
        self.pageid = pageid
        self.snippet = snippet
        self.section = section

    def to_json(self):
        return {
            "namespace": self.namespace,
            "title": self.title,
            "pageid": self.pageid,
            "snippet": self.snippet,
            "section": self.section,
        }

    def __repr__(self):
        return json.dumps(self.to_json(), indent=4)

    def __str__(self):
        return json.dumps(self.to_json(), indent=4)