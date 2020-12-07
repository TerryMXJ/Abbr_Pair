#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from javalang.ast import Node
from javalang.tree import *


class HashGenerator:
    def __init__(self) -> None:
        pass

    # def generate

    def generate_fingerprint(self, node: Node) -> str:
        strs = []
        node_str = type(node).__name__
        if isinstance(node, MethodInvocation):
            node_str += f":{node.member}@{len(node.arguments)}"
        elif isinstance(node, ClassCreator):
            node_str += f":{node.type}:{len(node.arguments)}"
        strs.append(node_str)
        return "@".join(strs)