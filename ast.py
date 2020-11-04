from dataclasses import dataclass


class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.leaf = leaf

    # instrukcje przypisania,
    # instrukcje warunkowe if-else,
    # pętle: while oraz for,
    # instrukcje break, continue oraz return,
    # instrukcje print,
    # instrukcje złożone,
    # tablice oraz ich zakresy.

@dataclass
class CompareExpr(Node):
    op: any
    left: any
    right: any

@dataclass
class BinExpr(Node):
    op: any
    left: any
    right: any


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
    return decorator

class TreePrinter:
    ...
    @addTiClass(BinExpr):
    def printTree(self.op):
        print(self.op)
        self.left.printTree(indent+1)
        self.left.printTree(indent+2)
    ...