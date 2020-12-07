#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from ..miner.abbr_base import AbbrBase

class MentionExtender:
    def __init__(self, abbr_base: AbbrBase):
        self.abbr_base = abbr_base

    def extend(self, mentions):
        pass
        