from src.type_checker.variables_types import Type


class Node:
    def __init__(self, position, children=None):
        self.position = position
        self.type = Type.UNKNOWN
        self.size = None

        if children:
            assert type(children) is list
            self.children = children
        else:
            self.children = []


class Program(Node):
    def __init__(self, position, statements_list):
        super().__init__(position, [statements_list])

        self.statements_list = statements_list


class Empty(Node):
    def __init__(self, position):
        super().__init__(position)


class Number(Node):
    def __init__(self, position, number):
        super().__init__(position, [number])

        self.number = number


class Expression(Node):
    def __init__(self, position, expression):
        super().__init__(position, [expression])

        self.expression = expression


class InnerVector(Node):
    def __init__(self, position, inner_vector, new_expression):
        super().__init__(position, [inner_vector + [new_expression]])

        self.inner_vector = inner_vector + [new_expression]

    def __add__(self, other):
        return self.inner_vector + other


class Vector(Node):
    def __init__(self, position, inner_vector):
        super().__init__(position, [inner_vector])

        self.inner_vector = inner_vector


class Matrix(Node):
    def __init__(self, position, matrix_type, argument):
        super().__init__(position, [matrix_type, argument])

        self.matrix_type = matrix_type
        self.argument = argument


class Range(Node):
    def __init__(self, position, from_index, to_index):
        super().__init__(position, [from_index, to_index])

        self.from_index = from_index
        self.to_index = to_index


class UnaryMinus(Node):
    def __init__(self, position, value):
        super().__init__(position, [value])

        self.value = value


class BinExpr(Node):
    def __init__(self, position, operator, left, right):
        super().__init__(position, [left, right])

        self.operator = operator
        self.left = left
        self.right = right


class MatrixBinExpr(Node):
    def __init__(self, position, operator, left, right):
        super().__init__(position, [left, right])

        self.operator = operator
        self.left = left
        self.right = right


class Transposition(Node):
    def __init__(self, position, matrix):
        super().__init__(position, [matrix])

        self.matrix = matrix


class CompareExpr(Node):
    def __init__(self, position, operator, left, right):
        super().__init__(position, [left, right])

        self.operator = operator
        self.left = left
        self.right = right


class SliceArgument(Node):
    def __init__(self, position, argument):
        super().__init__(position, [argument])

        self.argument = argument


class Slice(Node):
    def __init__(self, position, identifier, slice_argument_1, slice_argument_2):
        super().__init__(position, [slice_argument_1, slice_argument_2])

        self.identifier = identifier
        self.slice_argument_1 = slice_argument_1
        self.slice_argument_2 = slice_argument_2


class SliceOrID(Node):
    def __init__(self, position, slice_or_id):
        super().__init__(position, [slice_or_id])

        self.slice_or_id = slice_or_id


class AssignExpr(Node):
    def __init__(self, position, operator, left, right):
        super().__init__(position, [left, right])

        self.operator = operator
        self.left = left
        self.right = right


class StatementsList(Node):
    def __init__(self, position, statements_list, new_statement):
        super().__init__(position, [statements_list + [new_statement]])

        self.statements_list = statements_list + [new_statement]

    def __add__(self, other):
        return self.statements_list + other


class Return(Node):
    def __init__(self, position, value):
        super().__init__(position, [value])

        self.value = value


class CodeBlock(Node):
    def __init__(self, position, statements_lists):
        super().__init__(position, [statements_lists])

        self.statements_list = statements_lists


class LoopStatement(Node):
    def __init__(self, position, instruction):
        super().__init__(position, [instruction])

        self.instruction = instruction


class For(Node):
    def __init__(self, position, iterator, loop_range, statement):
        super().__init__(position, [loop_range, statement])

        self.iterator = iterator
        self.loop_range = loop_range
        self.statement = statement


class While(Node):
    def __init__(self, position, condition, statement):
        super().__init__(position, [condition, statement])

        self.condition = condition
        self.statement = statement


class If(Node):
    def __init__(self, position, condition, if_statement, else_statement):
        super().__init__(position, [condition, if_statement, else_statement])

        self.condition = condition
        self.if_statement = if_statement
        self.else_statement = else_statement


class Print(Node):
    def __init__(self, position, value):
        super().__init__(position, [value])

        self.value: InnerVector = value
