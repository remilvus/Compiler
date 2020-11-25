from ast import *
from scope_manager import *

class NodeVisitor(object):

    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node : Node):
       for child in node.children:
           self.visit(child)


class TypeChecker(NodeVisitor):

    def visit_BinExpr(self, node) -> VariableSymbol:
        # alternative usage,
        # requires definition of accept method in class Node
        type1 = self.visit(node.left)  # type1 = node.left.accept(self)
        type2 = self.visit(node.right)  # type2 = node.right.accept(self)
        op = node.op

    def visit_Program(self, node : Program):
        self.visit(node.statements_list)

    def visit_Variable(self, node):
        pass

    def visit_SliceOrID(self, node):
        if type(node) is Node:
            pass
        else:
            pass
