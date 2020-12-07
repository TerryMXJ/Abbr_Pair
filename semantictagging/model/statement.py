#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class Statement:
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.ast = None
        self.fingerprint = -1