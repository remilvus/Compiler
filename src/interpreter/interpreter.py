from src.ast.ast import *
from src.type_checker.variables_types import Type
from src.interpreter.visit import *
from src.interpreter.memory import *
from src.interpreter.exceptions import ReturnValueException, BreakException, ContinueException
from src.type_checker.node_visitor import possible_operations
import numpy as np
from functools import reduce
import operator


# todo check types
class Interpreter(object):
    def __init__(self):
        self.memory_stack = MemoryStack()
        self.operators = {"+": operator.add,
                          "-": operator.sub,
                          "/": operator.truediv,
                          "*": operator.mul,
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
    def visit(self, node: Empty):
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
        inner = self.visit(node.inner_vector)

        if reduce(lambda x, y: x and isinstance(y, np.ndarray), inner, True):
            # matrix
            return np.stack(inner)
        elif reduce(lambda x, y: x and (isinstance(y, int) or isinstance(y, float)), inner, True):
            # vector
            return np.array(inner)
        else:
            # todo is it possible to be here?
            return inner.value

    @when(Matrix)
    def visit(self, node: Matrix):
        size = self.visit(node.argument)
        matrix_type = node.matrix_type.lower()

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

        return slice(from_index, to_index)

    @when(UnaryMinus)
    def visit(self, node: UnaryMinus):
        return -self.visit(node.value)

    @when(BinExpr)
    def visit(self, node: BinExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        bin_operator = node.operator

        if bin_operator == "*" and isinstance(left, np.ndarray) and isinstance(right, np.ndarray):
            return left @ right
        else:
            return self.operators[bin_operator](left, right)

    @when(MatrixBinExpr)
    def visit(self, node: MatrixBinExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        bin_operator = node.operator

        return self.operators[bin_operator](left, right)

    @when(Transposition)
    def visit(self, node: Transposition):
        matrix = self.visit(node.matrix)
        return np.transpose(matrix)

    @when(CompareExpr)
    def visit(self, node: CompareExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        bin_operator = node.operator

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
        size = value.shape

        if type(node.slice_argument_1) == int and (node.slice_argument_1 >= size[0] or node.slice_argument_1 < 0):
            raise IndexError(f"index {node.slice_argument_1} is out of bounds for axis 0 with size {size[0]}")

        if node.slice_argument_2 is not None:
            if type(node.slice_argument_2) == int and (node.slice_argument_2 >= size[1] or node.slice_argument_2 < 0):
                raise IndexError(f"index {node.slice_argument_2} is out of bounds for axis 1 with size {size[1]}")

            value = value[node.slice_argument_1, node.slice_argument_2]
        else:
            value = value[node.slice_argument_1]

        return value

    @when(SliceOrID)
    def visit(self, node: SliceOrID):
        if isinstance(node.slice_or_id, Slice):
            return self.visit(node.slice_or_id)
        else:
            # todo temporary solution
            try:
                return self.memory_stack.get(node.slice_or_id)
            except KeyError:
                return None

    @when(AssignExpr)
    def visit(self, node: AssignExpr):
        left = node.left.slice_or_id
        left_value = self.visit(node.left)  # todo can be none?
        right_value = self.visit(node.right)
        op = node.operator

        if len(op) == 2:
            bin_op = op[0]
            right_value = self.operators[bin_op](left_value, right_value)

        if isinstance(left, Slice):
            new_vector = self.memory_stack.get(left.identifier)
            size = new_vector.shape

            if type(left.slice_argument_1) == int and (left.slice_argument_1 >= size[0] or left.slice_argument_1 < 0):
                raise IndexError(f"index {left.slice_argument_1} is out of bounds for axis 0 with size {size[0]}")

            if left.slice_argument_2 is not None:
                if type(left.slice_argument_2) == int and \
                        (left.slice_argument_2 >= size[1] or left.slice_argument_2 < 0):
                    raise IndexError(f"index {left.slice_argument_2} is out of bounds for axis 1 with size {size[1]}")

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
