from src.ast.ast import *


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
        self.statements_list.print_tree(indent)

    @staticmethod
    @add_to_class(Empty)
    def print_tree(self, indent=0):
        pass

    @staticmethod
    @add_to_class(Number)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.number)

    @staticmethod
    @add_to_class(Expression)
    def print_tree(self, indent=0):
        if isinstance(self.expression, Node):
            self.expression.print_tree(indent)
        else:
            print_indent(indent)
            print(self.expression)

    @staticmethod
    @add_to_class(InnerVector)
    def print_tree(self, indent=0):
        for element in self.inner_vector:
            element.print_tree(indent)

    @staticmethod
    @add_to_class(Vector)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("VECTOR")

        self.inner_vector.print_tree(indent + 1)

    @staticmethod
    @add_to_class(Matrix)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.matrix_type)

        self.argument.print_tree(indent + 1)

    @staticmethod
    @add_to_class(Range)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("RANGE")

        self.from_index.print_tree(indent + 1)
        self.to_index.print_tree(indent + 1)

    @staticmethod
    @add_to_class(UnaryMinus)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("-")

        self.value.print_tree(indent + 1)

    @staticmethod
    @add_to_class(BinExpr)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.operator)

        self.left.print_tree(indent + 1)
        self.right.print_tree(indent + 1)

    @staticmethod
    @add_to_class(MatrixBinExpr)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.operator)

        self.left.print_tree(indent + 1)
        self.right.print_tree(indent + 1)

    @staticmethod
    @add_to_class(Transposition)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("TRANSPOSE")

        self.matrix.print_tree(indent + 1)

    @staticmethod
    @add_to_class(CompareExpr)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.operator)

        self.left.print_tree(indent + 1)
        self.right.print_tree(indent + 1)

    @staticmethod
    @add_to_class(SliceArgument)
    def print_tree(self, indent=0):
        self.argument.print_tree(indent)

    @staticmethod
    @add_to_class(Slice)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("REF")

        print_indent(indent + 1)
        print(self.identifier)

        self.slice_argument_1.print_tree(indent + 1)
        if self.slice_argument_2:
            self.slice_argument_2.print_tree(indent + 1)

    @staticmethod
    @add_to_class(SliceOrID)
    def print_tree(self, indent=0):
        if isinstance(self.slice_or_id, Node):
            self.slice_or_id.print_tree(indent)
        else:
            print_indent(indent)
            print(self.slice_or_id)

    @staticmethod
    @add_to_class(AssignExpr)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.operator)

        self.left.print_tree(indent + 1)
        self.right.print_tree(indent + 1)

    @staticmethod
    @add_to_class(StatementsList)
    def print_tree(self, indent=0):
        for statement in self.statements_list:
            statement.print_tree(indent)

    @staticmethod
    @add_to_class(Return)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("RETURN")

        if self.value:
            self.value.print_tree(indent + 1)

    @staticmethod
    @add_to_class(CodeBlock)
    def print_tree(self, indent=0):
        self.statements_list.print_tree(indent)

    @staticmethod
    @add_to_class(LoopStatement)
    def print_tree(self, indent=0):
        print_indent(indent)
        print(self.instruction.upper())

    @staticmethod
    @add_to_class(For)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("FOR")

        print_indent(indent + 1)
        print(self.iterator)

        self.loop_range.print_tree(indent + 1)
        self.statement.print_tree(indent + 1)

    @staticmethod
    @add_to_class(While)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("WHILE")

        self.condition.print_tree(indent + 1)
        self.statement.print_tree(indent + 1)

    @staticmethod
    @add_to_class(If)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("IF")
        self.condition.print_tree(indent + 1)

        print_indent(indent)
        print("THEN")
        self.if_statement.print_tree(indent + 1)

        if self.else_statement:
            print_indent(indent)
            print("ELSE")
            self.else_statement.print_tree(indent + 1)

    @staticmethod
    @add_to_class(Print)
    def print_tree(self, indent=0):
        print_indent(indent)
        print("PRINT")

        self.value.print_tree(indent + 1)
