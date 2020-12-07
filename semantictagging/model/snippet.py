#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import List
from semantictagging.code_element.statement import Statement


class Snippet:
    def __init__(self, code):
        self.code = code
        self.tokens = list()
        self.ast = None
        self.stmts = list()

    def add_stmt(self, stmt: Statement):
        self.stmts.append(stmt)