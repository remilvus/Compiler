from src.ast.ast import *
from src.type_checker.variables_types import Type
from src.interpreter.visit import *
from src.interpreter.memory import *
from src.type_checker.node_visitor import possible_operations
import numpy as np
from functools import reduce
import operator

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
        #  self.memory.push_scope("program")
        self.visit(node.statements_list)
    #   self.memory.pop_scope()

    @when(Empty)
    def visit(self, node: Empty):
        pass

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

        if reduce(lambda x,y: x and isinstance(y, np.ndarray), inner, True):
            # matrix
            return np.stack(inner)
        elif reduce(lambda x,y: x and (isinstance(y, int) or isinstance(y, float)),
                    inner,
                    True):
            return np.array(inner)
        else:
            # vector
            return inner.value

    @when(Matrix)
    def visit(self, node: Matrix):
        size = self.visit(node.argument)
        type = node.matrix_type.lower()

        if type == "eye":
            shape = size
        else:
            shape = (size, size)
        return {"ones": np.ones,
                "zeros": np.zeros,
                "eye": np.eye}[type](shape, dtype=np.float)

    @when(Range)
    def visit(self, node: Range):
        from_index = self.visit(node.from_index)
        to_index = self.visit(node.to_index)
        return range(from_index, to_index)

    @when(UnaryMinus)
    def visit(self, node: UnaryMinus):
        return -self.visit(node.value)

    @when(BinExpr)
    def visit(self, node: BinExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        operator = node.operator

        if operator == "*" and isinstance(left, np.ndarray) and isinstance(right, np.ndarray):
            return left @ right
        else:
            return self.operators[operator](left, right)

    @when(MatrixBinExpr)
    def visit(self, node: MatrixBinExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        operator = node.operator

        return self.operators[operator](left, right)

    @when(Transposition)
    def visit(self, node: Transposition):
        matrix = self.visit(node.matrix)
        return np.transpose(matrix)

    @when(CompareExpr)
    def visit(self, node: CompareExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        operator = node.operator

        return self.comparison_operators[operator](left, right)

    @when(SliceArgument)
    def visit(self, node: SliceArgument):
        pass
        # todo

    @when(Slice)
    def visit(self, node: Slice):
        pass
        # todo

    @when(SliceOrID)
    def visit(self, node: SliceOrID):
        if type(node.slice_or_id) is str:  # id
            node.id = node.slice_or_id
            try:
                return self.memory_stack.get(node.slice_or_id)
            except KeyError:
                pass
        else:
            # slice
            pass #todo
            # visit

    @when(AssignExpr)
    def visit(self, node: AssignExpr):
        left_value = self.visit(node.left) # may be none
        left = node.left.id
        right = self.visit(node.right)
        op = node.operator

        if len(op) == 2:
            bin_op = op[0]
            assert type(left_value) is not None
            right = self.operators[bin_op](left_value, right)

        if type(left) is str:  # id
            self.memory_stack.set(left, right)
        else:
            assert type(node.left) is Slice
            # todo
            raise NotImplemented


    @when(StatementsList)
    def visit(self, node: StatementsList):
        for statement in node.statements_list:
            self.visit(statement)

    @when(Return)
    def visit(self, node: Return):
        pass
        # todo

    @when(CodeBlock)
    def visit(self, node: CodeBlock):
        pass
        # todo

    @when(LoopStatement)
    def visit(self, node: LoopStatement):
        pass
        # todo

    @when(For)
    def visit(self, node: For):
        pass
        # todo

    @when(While)
    def visit(self, node: While):
        pass
        # todo

    @when(If)
    def visit(self, node: If):
        pass
        # todo

    @when(Print)
    def visit(self, node: Print):
        values = self.visit(node.value)
        print(", ".join(map(str, values)))
