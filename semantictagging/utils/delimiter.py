#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import functools
import re

class Delimiter:

    @staticmethod
    @functools.lru_cache(maxsize=10000)
    def split_camel(camel_case: str, to_lower=True):
        delimited_case = camel_case.replace('...', '-DOTDOTDOT-')
        delimited_case = delimited_case.split('.')[-1]
        delimited_case = delimited_case.replace('[]', ' []')
        delimited_case = delimited_case.replace('-DOTDOTDOT-', ' ...')
        delimited_case = re.sub(r'_', " ", delimited_case).strip()
        delimited_case = re.sub(
            r'([A-Za-z])([Vv][0-9]+)([A-Za-z]|$)', r'\1 \2 \3', delimited_case)
        delimited_case = re.sub(
            r'([A-Za-z])([0-9]+D)([A-Z]|$)', r'\1 \2 \3', delimited_case)
        delimited_case = re.sub(r'([A-Z][0-9]?)(to)([A-Z]|$)',
                           r'\1 \2 \3', delimited_case)
        delimited_case = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', delimited_case)
        delimited_case = re.sub(r'([A-Z]+)', r' \1', delimited_case)
        delimited_case = re.sub(
            r'([A-UW-Za-uw-z])(2)([A-Za-z]|\s)', r'\1 To \3', delimited_case)
        delimited_case = re.sub(r'\s+', ' ', delimited_case)
        delimited_case = re.sub(
            r'([A-UW-Za-uw-z])(4)([A-Za-z]|\s)', r'\1 For \3', delimited_case)
        delimited_case = re.sub(r'\s+', ' ', delimited_case)
        delimited_case = re.sub(r'([A-Za-z]) ([Vv][0-9]+)', r'\1\2', delimited_case)
        delimited_case = re.sub(
            r'(\s|^|[A-Z])([0-9]+) ([A-Z])', r'\1\2\3', delimited_case)
        delimited_case = delimited_case.strip()

        if to_lower:
            delimited_case = delimited_case.lower()
        return delimited_case