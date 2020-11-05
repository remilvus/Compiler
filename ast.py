from dataclasses import dataclass


class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.leaf = leaf

    # pętle: while oraz for,
    # instrukcje break, continue oraz return,
    # instrukcje złożone,
    # tablice oraz ich zakresy.


# Instructions
@dataclass
class ReturnInstruction(Node):
    value: any


@dataclass
class LoopInstruction(Node):
    instruction: any


@dataclass
class PrintInstruction(Node):
    value: any


@dataclass
class If(Node):
    condition: any
    if_block: any
    else_block: any


# Arithmetic
@dataclass
class AssignExpr(Node):
    op: any
    left: any
    right: any


@dataclass
class BinExpr(Node):
    op: any
    left: any
    right: any\

@dataclass
class MatrixBinExpr(Node):
    op: any
    left: any
    right: any


@dataclass
class UnaryMinus(Node):
    value: any


@dataclass
class CompareExpr(Node):
    op: any
    left: any
    right: any


@dataclass
class Transposition(Node):
    matrix: any

def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
    return decorator

# class TreePrinter:
#     ...
#     @addToClass(BinExpr)
#     def printTree(self.op):
#         print(self.op)
#         self.left.printTree(indent+1)
#         self.left.printTree(indent+2)
#     ...