from src.ast.ast import *
from src.type_checker.variables_types import Type
from src.type_checker.node_visitor import valid_operations
from src.interpreter.visit import *
from src.interpreter.memory import *
from src.interpreter.exceptions import ReturnValueException, BreakException, ContinueException
import numpy as np
from functools import reduce
import operator
import sys


class Interpreter(object):
    def __init__(self):
        self.memory_stack = MemoryStack()
        self.operators = {"+": operator.add,
                          "-": operator.sub,
                          "/": operator.truediv,
                          "*": lambda left, right: left @ right if Type.get_type(left) == Type.MATRIX else left * right,
                          ".+": operator.add,
                          ".-": operator.sub,
                          "./": operator.truediv,
                          ".*": operator.mul
                          }

        self.comparison_operators = {"==": operator.eq,
                                     "!=": operator.ne,
                                     "<": operator.lt,
                                     "<=": operator.le,
                                     ">": operator.gt,
                                     ">=": operator.ge
                                     }

    def generic_visit(self, node: Node):
        for child in node.children:
            if child:
                self.visit(child)

    @on('node')
    def visit(self, node):
        """
        This is the generic method that initializes the
        dynamic dispatcher.
        """

    @when(Program)
    def visit(self, node: Program):
        try:
            self.visit(node.statements_list)
            return None
        except ReturnValueException as exception:
            return exception.value

    @when(Empty)
    def visit(self, _):
        return None

    @when(Number)
    def visit(self, node: Number):
        return node.number

    @when(Expression)
    def visit(self, node: Expression):
        if Type.get_type(node.expression) == Type.STRING:
            return node.expression
        else:
            return self.visit(node.expression)

    @when(InnerVector)
    def visit(self, node: InnerVector):
        return [self.visit(expression) for expression in node.inner_vector]

    @when(Vector)
    def visit(self, node: InnerVector):
        vector = self.visit(node.inner_vector)

        if len(vector) != 0:
            vector_type = Type.get_type(vector[0])
            for element in vector:
                if Type.get_type(element) != vector_type:
                    error(f"vector elements should be of the same type. " +
                          f"Found types: {vector_type} and {Type.get_type(element)}", node)

            # vector is a matrix
            if vector_type == Type.VECTOR:
                for row in vector:
                    if type(row) is list:
                        error(f"cannot make matrix with strings", node)

                row_size = vector[0].shape
                row_type = None

                for row in vector:
                    if row.shape != row_size:
                        error("matrix has rows with different sizes", node)

                    if row.shape[0] != 0 and row_type is None:
                        row_type = Type.get_type(row[0])
                    elif row_type is not None and Type.get_type(row[0]) != row_type:
                        error(f"matrix elements should be of the same type. " +
                              f"Found types: {row_type} and {Type.get_type(row[0])}", node)

        # matrix
        if reduce(lambda x, y: x and isinstance(y, np.ndarray), vector, True):
            return np.stack(vector)
        # vector
        elif reduce(lambda x, y: x and (isinstance(y, int) or isinstance(y, float)), vector, True):
            return np.array(vector)
        # list of strings
        else:
            return vector

    @when(Matrix)
    def visit(self, node: Matrix):
        size = self.visit(node.argument)
        matrix_type = node.matrix_type.lower()

        if Type.get_type(size) != Type.INTNUM:
            error(f"size of '{matrix_type}' matrix should be an integer. Found: {Type.get_type(size)}", node)

        if matrix_type == "eye":
            shape = size
        else:
            shape = (size, size)

        return {"ones": np.ones,
                "zeros": np.zeros,
                "eye": np.eye}[matrix_type](shape, dtype=np.float)

    @when(Range)
    def visit(self, node: Range):
        from_index = self.visit(node.from_index)
        to_index = self.visit(node.to_index)

        range_types = (Type.get_type(from_index), Type.get_type(to_index))
        if range_types[0] != Type.INTNUM or range_types[1] != Type.INTNUM:
            error(f"Range should contain only integers. Found: {range_types[0]} and {range_types[1]}", node)

        return slice(from_index, to_index)

    @when(UnaryMinus)
    def visit(self, node: UnaryMinus):
        value = self.visit(node.value)
        value_type = Type.get_type(value)

        if value_type in valid_operations and "-" in valid_operations[value_type]:
            return -value
        else:
            error(f"negation is possible only for numbers. Found: {value_type}", node.value)

    @when(BinExpr)
    def visit(self, node: BinExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        bin_operator = node.operator

        expression_type = (Type.get_type(left), Type.get_type(right))
        if expression_type not in valid_operations or bin_operator not in valid_operations[expression_type]:
            error(f"invalid types in binary expression. Left type: {expression_type[0]}, " +
                  f"right type: {expression_type[1]}", node)

        if expression_type == (Type.MATRIX, Type.MATRIX) and bin_operator == "*" and left.shape[1] != right.shape[0]:
            error(f"incompatible matrices sizes in matrix multiplication. Found {left.shape} and {right.shape}",
                  node.right)

        return self.operators[bin_operator](left, right)

    @when(MatrixBinExpr)
    def visit(self, node: MatrixBinExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        bin_operator = node.operator

        expression_type = (Type.get_type(left), Type.get_type(right))
        if expression_type not in valid_operations or bin_operator not in valid_operations[expression_type]:
            error(f"matrix binary operations can be made only on matrices and vectors. Found {expression_type[0]} " +
                  f"and {expression_type[1]}", node)

        if left.shape != right.shape:
            error(f"incompatible sizes within operation: '{bin_operator}'. Found: {left.shape} and {right.shape}, " +
                  "but they should be equal", node)

        return self.operators[bin_operator](left, right)

    @when(Transposition)
    def visit(self, node: Transposition):
        matrix = self.visit(node.matrix)

        if Type.get_type(matrix) == Type.MATRIX:
            return np.transpose(matrix)
        else:
            error(f"only matrix can be transposed. Found: {Type.get_type(matrix)}", node)

    @when(CompareExpr)
    def visit(self, node: CompareExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        bin_operator = node.operator

        expression_type = (Type.get_type(left), Type.get_type(right))
        if expression_type not in valid_operations or bin_operator not in valid_operations[expression_type]:
            error(f"incompatible types for comparison. Found {expression_type[0]} and {expression_type[1]}", node)

        return self.comparison_operators[bin_operator](left, right)

    @when(SliceArgument)
    def visit(self, node: SliceArgument):
        return self.visit(node.argument)

    @when(Slice)
    def visit(self, node: Slice):
        node.slice_argument_1 = self.visit(node.slice_argument_1)

        if node.slice_argument_2:
            node.slice_argument_2 = self.visit(node.slice_argument_2)

        value = self.memory_stack.get(node.identifier)

        if Type.get_type(value) not in {Type.VECTOR, Type.MATRIX}:
            error(f"only vectors and matrices can be sliced, found {Type.get_type(value)}", node)

        size = (len(value),) if type(value) == list else value.shape

        if type(node.slice_argument_1) == int and (node.slice_argument_1 >= size[0] or node.slice_argument_1 < 0):
            error(f"index {node.slice_argument_1} is out of bounds for axis 0 with size {size[0]}", node)
        elif type(node.slice_argument_1) not in {int, slice}:
            error(f"first slice argument should be integer or slice, found: {type(node.slice_argument_1)}", node)
        elif type(node.slice_argument_1) == slice:
            if node.slice_argument_1.start < 0 or node.slice_argument_1.start > size[0] or \
                    node.slice_argument_1.stop < 0 or node.slice_argument_1.stop > size[0]:
                error(f"slice {(node.slice_argument_1.start, node.slice_argument_1.stop)} " +
                      f"is out of bounds for axis 0 with size {size[0]}", node)

        if node.slice_argument_2 is not None:
            if len(size) < 2:
                error(f"2D slicing can be made only on matrices", node)

            if type(node.slice_argument_2) == int and (node.slice_argument_2 >= size[1] or node.slice_argument_2 < 0):
                error(f"index {node.slice_argument_1} is out of bounds for axis 1 with size {size[1]}", node)
            elif type(node.slice_argument_2) not in {int, slice}:
                error(f"second slice argument should be integer or slice, found: {type(node.slice_argument_2)}", node)
            elif type(node.slice_argument_2) == slice:
                if node.slice_argument_2.start < 0 or node.slice_argument_2.start > size[1] or \
                        node.slice_argument_2.stop < 0 or node.slice_argument_2.stop > size[1]:
                    error(f"slice {(node.slice_argument_2.start, node.slice_argument_2.stop)} " +
                          f"is out of bounds for axis 1 with size {size[1]}", node)

            value = value[node.slice_argument_1, node.slice_argument_2]
        else:
            value = value[node.slice_argument_1]

        return value

    @when(SliceOrID)
    def visit(self, node: SliceOrID):
        if isinstance(node.slice_or_id, Slice):
            return self.visit(node.slice_or_id)
        else:
            return self.memory_stack.get(node.slice_or_id)

    @when(AssignExpr)
    def visit(self, node: AssignExpr):
        left = node.left.slice_or_id
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        op = node.operator

        if len(op) == 2:
            bin_operator = op[0]

            expression_type = (Type.get_type(left_value), Type.get_type(right_value))
            if expression_type not in valid_operations or bin_operator not in valid_operations[expression_type]:
                error(f"invalid types in binary expression. Left type: {expression_type[0]}, " +
                      f"right type: {expression_type[1]}", node)

            right_value = self.operators[bin_operator](left_value, right_value)

        if isinstance(left, Slice):
            new_vector = self.memory_stack.get(left.identifier)

            if left.slice_argument_2 is not None:
                new_vector[left.slice_argument_1, left.slice_argument_2] = right_value
            else:
                new_vector[left.slice_argument_1] = right_value

            self.memory_stack.set(left.identifier, new_vector)
        else:
            self.memory_stack.set(left, right_value)

        return None

    @when(StatementsList)
    def visit(self, node: StatementsList):
        for statement in node.statements_list:
            self.visit(statement)

        return None

    @when(Return)
    def visit(self, node: Return):
        raise ReturnValueException(node.value)

    @when(CodeBlock)
    def visit(self, node: CodeBlock):
        return self.visit(node.statements_list)

    @when(LoopStatement)
    def visit(self, node: LoopStatement):
        if node.instruction.lower() == "break":
            raise BreakException
        else:
            raise ContinueException

    @when(For)
    def visit(self, node: For):
        from_index = self.visit(node.loop_range.from_index)
        to_index = self.visit(node.loop_range.to_index)

        range_types = (Type.get_type(from_index), Type.get_type(to_index))
        if range_types[0] != Type.INTNUM or range_types[1] != Type.INTNUM:
            error(f"Range should contain only integers. Found: {range_types[0]} and {range_types[1]}", node)

        for i in range(from_index, to_index):
            self.memory_stack.push("for")
            self.memory_stack.set(node.iterator, i)

            try:
                self.visit(node.statement)
            except BreakException:
                break
            except ContinueException:
                pass
            finally:
                self.memory_stack.pop()

        return None

    @when(While)
    def visit(self, node: While):
        while self.visit(node.condition):
            self.memory_stack.push("while")
            try:
                self.visit(node.statement)
            except BreakException:
                break
            except ContinueException:
                pass
            self.memory_stack.pop()

        return None

    @when(If)
    def visit(self, node: If):
        if self.visit(node.condition):
            self.visit(node.if_statement)
        elif node.else_statement:
            self.visit(node.else_statement)

        return None

    @when(Print)
    def visit(self, node: Print):
        values = self.visit(node.value)
        print(", ".join(map(str, values)))


def error(message, node):
    print(f"Runtime error: {message}, {node.position}")
    sys.exit()
