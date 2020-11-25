class Node:
    def __init__(self, children=None, leaf=None):
        # self.type = type
        if children:
            assert type(children) is list
            self.children = children
        else:
            self.children = []
        # self.leaf = leaf


class Program(Node):
    def __init__(self, statements_list):
        super().__init__([statements_list])

        self.statements_list = statements_list


class Empty(Node):
    def __init__(self):
        super().__init__()


class Number(Node):
    def __init__(self, number):
        super().__init__([number])

        self.number = number


class Expression(Node):
    def __init__(self, expression):
        super().__init__([expression])

        self.expression = expression


class InnerVector(Node):
    def __init__(self, inner_vector, new_expression):
        super().__init__([inner_vector, new_expression])

        self.inner_vector = inner_vector
        self.new_expression = new_expression


class Vector(Node):
    def __init__(self, inner_vector):
        super().__init__([inner_vector])

        self.inner_vector = inner_vector


class Matrix(Node):
    def __init__(self, matrix_type, argument):
        super().__init__([matrix_type, argument])

        self.matrix_type = matrix_type
        self.argument = argument


class Range(Node):
    def __init__(self, from_index, to_index):
        super().__init__([from_index, to_index])

        self.from_index = from_index
        self.to_index = to_index


class UnaryMinus(Node):
    def __init__(self, value):
        super().__init__([value])

        self.value = value


class BinExpr(Node):
    def __init__(self, operator, left, right):
        super().__init__([operator, left, right])

        self.operator = operator
        self.left = left
        self.right = right


class MatrixBinExpr(Node):
    def __init__(self, operator, left, right):
        super().__init__([operator, left, right])

        self.operator = operator
        self.left = left
        self.right = right


class Transposition(Node):
    def __init__(self, matrix):
        super().__init__([matrix])

        self.matrix = matrix


class CompareExpr(Node):
    def __init__(self, operator, left, right):
        super().__init__([operator, left, right])

        self.operator = operator
        self.left = left
        self.right = right


class SliceArgument(Node):
    def __init__(self, argument):
        super().__init__([argument])

        self.argument = argument


class Slice(Node):
    def __init__(self, identifier, slice_argument_1, slice_argument_2):
        super().__init__([identifier, slice_argument_1, slice_argument_2])

        self.identifier = identifier
        self.slice_argument_1 = slice_argument_1
        self.slice_argument_2 = slice_argument_2


class SliceOrID(Node):
    def __init__(self, slice_or_id):
        super().__init__([slice_or_id])

        self.slice_or_id = slice_or_id


class AssignExpr(Node):
    def __init__(self, operator, left, right):
        super().__init__([operator, left, right])

        self.operator = operator
        self.left = left
        self.right = right


class StatementsList(Node):
    def __init__(self, statements_list, new_statement):
        super().__init__([statements_list, new_statement])

        self.statements_list = statements_list
        self.new_statement = new_statement


class Return(Node):
    def __init__(self, value):
        super().__init__([value])

        self.value = value


class CodeBlock(Node):
    def __init__(self, statements_lists):
        super().__init__([statements_lists])

        self.statements_list = statements_lists


class LoopStatement(Node):
    def __init__(self, instruction):
        super().__init__([instruction])

        self.instruction = instruction


class For(Node):
    def __init__(self, iterator, loop_range, statement):
        super().__init__([iterator, loop_range, statement])

        self.iterator = iterator
        self.loop_range = loop_range
        self.statement = statement


class While(Node):
    def __init__(self, condition, statement):
        super().__init__([condition, statement])

        self.condition = condition
        self.statement = statement


class If(Node):
    def __init__(self, condition, if_statement, else_statement):
        super().__init__([condition, if_statement, else_statement])

        self.condition = condition
        self.if_statement = if_statement
        self.else_statement = else_statement


class Print(Node):
    def __init__(self, value):
        super().__init__([value])

        self.value = value
