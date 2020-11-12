from ast import *


def add_to_class(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
    return decorator


def print_indent(indent):
    for i in range(indent):
        print("|  ", end="")


class TreePrinter:
    def __init__(self):
        pass

    @staticmethod
    @add_to_class(Program)
    def print_tree(self, indent=0):
        self.children[0].print_tree(indent)

    @staticmethod
    @add_to_class(Empty)
    def print_tree(self, indent=0):
        pass

    @staticmethod
    @add_to_class(Number)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.children[0])

    @staticmethod
    @add_to_class(Expression)
    def print_tree(self, indent=0):
        if isinstance(self.children[0], Node):
            self.children[0].print_tree(indent)
        else:
            print_indent(indent)
            print(self.children[0])

    @staticmethod
    @add_to_class(InnerVector)
    def print_tree(self, indent=0):
        if self.children[0]:
            self.children[0].print_tree(indent)
        self.children[1].print_tree(indent)

    @staticmethod
    @add_to_class(Vector)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("VECTOR")

        self.children[0].print_tree(indent+1)

    @staticmethod
    @add_to_class(Matrix)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.children[0])

        self.children[1].print_tree(indent+1)

    @staticmethod
    @add_to_class(Range)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("RANGE")

        self.children[0].print_tree(indent + 1)
        self.children[1].print_tree(indent + 1)

    @staticmethod
    @add_to_class(UnaryMinus)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("-")

        self.children[0].print_tree(indent + 1)

    @staticmethod
    @add_to_class(BinExpr)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.children[0])

        self.children[1].print_tree(indent+1)
        self.children[2].print_tree(indent+1)

    @staticmethod
    @add_to_class(MatrixBinExpr)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.children[0])

        self.children[1].print_tree(indent + 1)
        self.children[2].print_tree(indent + 1)

    @staticmethod
    @add_to_class(Transposition)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("TRANSPOSE")

        self.children[0].print_tree(indent + 1)

    @staticmethod
    @add_to_class(CompareExpr)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.children[0])

        self.children[1].print_tree(indent + 1)
        self.children[2].print_tree(indent + 1)

    @staticmethod
    @add_to_class(SliceArgument)
    def print_tree(self, indent=0):
        self.children[0].print_tree(indent)

    @staticmethod
    @add_to_class(Slice)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("REF")

        print_indent(indent+1)
        print(self.children[0])

        self.children[1].print_tree(indent+1)
        if self.children[2]:
            self.children[2].print_tree(indent+1)

    @staticmethod
    @add_to_class(SliceOrID)
    def print_tree(self, indent=0):
        if isinstance(self.children[0], Node):
            self.children[0].print_tree(indent)
        else:
            print_indent(indent)
            print(self.children[0])

    @staticmethod
    @add_to_class(AssignExpr)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.children[0])

        self.children[1].print_tree(indent + 1)
        self.children[2].print_tree(indent + 1)

    @staticmethod
    @add_to_class(StatementsList)
    def print_tree(self, indent=0):
        if self.children[0]:
            self.children[0].print_tree(indent)

        self.children[1].print_tree(indent)

    @staticmethod
    @add_to_class(Return)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("RETURN")

        if self.children[0]:
            self.children[0].print_tree(indent+1)

    @staticmethod
    @add_to_class(CodeBlock)
    def print_tree(self, indent=0):
        self.children[0].print_tree(indent)

    @staticmethod
    @add_to_class(LoopStatement)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.children[0].upper())

    @staticmethod
    @add_to_class(For)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("FOR")

        print_indent(indent + 1)
        print(self.children[0])

        self.children[1].print_tree(indent + 1)
        self.children[2].print_tree(indent + 1)

    @staticmethod
    @add_to_class(While)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("WHILE")

        self.children[0].print_tree(indent + 1)
        self.children[1].print_tree(indent + 1)

    @staticmethod
    @add_to_class(If)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("IF")
        self.children[0].print_tree(indent + 1)

        print_indent(indent)
        print("THEN")
        self.children[1].print_tree(indent + 1)

        if self.children[2]:
            print_indent(indent)
            print("ELSE")
            self.children[2].print_tree(indent + 1)

    @staticmethod
    @add_to_class(Print)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("PRINT")

        self.children[0].print_tree(indent + 1)
