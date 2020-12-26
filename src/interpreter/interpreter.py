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
                          ".*": operator.mul}

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

    @when(StatementsList)
    def visit(self, node: StatementsList):
        for statement in node.statements_list:
            self.visit(statement)

    @when(Number)
    def visit(self, node: Number):
        node.value = node.number
        node.type = Type.get_type(node.number)

    @when(Expression)
    def visit(self, node: Expression):
        if Type.get_type(node.expression) == Type.STRING:
            node.value = node.expression
        else:
            self.visit(node.expression)
            node.value = node.expression.value

    @when(InnerVector)
    def visit(self, node: InnerVector):
        node.value = []
        for expression in node.inner_vector:
            self.visit(expression)
            node.value.append(expression.value)

    @when(Vector)
    def visit(self, node: InnerVector):
        self.visit(node.inner_vector)
        inner = node.inner_vector

        if reduce(lambda x,y: x and isinstance(y, np.ndarray), inner.value, True):
            # matrix
            node.value = np.stack(inner.value)
        elif reduce(lambda x,y: x and (isinstance(y, int) or isinstance(y, float)),
                    inner.value,
                    True):
            node.value = np.array(inner.value)
        else:
            # vector
            node.value = inner.value

    @when(Matrix)
    def visit(self, node: Matrix):
        self.generic_visit(node)

        size = node.argument.value
        type = node.matrix_type.lower()
        if type == "eye":
            shape = size
        else:
            shape = (size, size)
        node.value = {"ones": np.ones,
                      "zeros": np.zeros,
                      "eye": np.eye}[type](shape, dtype=np.float)

    @when(AssignExpr)
    def visit(self, node: AssignExpr):
        self.generic_visit(node)

        if type(node.left.slice_or_id) is str:  # id
            self.memory_stack.set(node.left.slice_or_id, node.right.value)
        else:
            assert type(node.left) is Slice
            # todo
            raise NotImplemented

    @when(BinExpr)
    def visit(self, node: BinExpr):
        self.generic_visit(node)

        left = node.left.value
        right = node.right.value
        if node.operator == "*" and isinstance(left, np.ndarray) and isinstance(right, np.ndarray):
            node.value = left @ right
        else:
            node.value = self.operators[node.operator](left, right)

    @when(MatrixBinExpr)
    def visit(self, node: MatrixBinExpr):
        self.generic_visit(node)

        left = node.left.value
        right = node.right.value
        node.value = self.operators[node.operator](left, right)

    @when(SliceOrID)
    def visit(self, node: SliceOrID):
        if type(node.slice_or_id) is str:  # id
            node.id = node.slice_or_id
            try:
                node.value = self.memory_stack.get(node.slice_or_id)
            except KeyError:
                pass
        else:
            # slice
            pass #todo
            # visit

    @when(Print)
    def visit(self, node: Print):
        self.generic_visit(node)
        print(", ".join(map(str, node.value.value)))

    # todo:
    # # simplistic while loop interpretation
    # @when(ast.WhileInstr)
    # def visit(self, node):
    #     r = None
    #     while node.cond.accept(self):
    #         r = node.body.accept(self)
    #     return r

    # def visit_range(self, node: Range):
    # def visit_unary_minus(self, node: UnaryMinus):
    # def visit_transposition(self, node: Transposition):
    # def visit_compare_expr(self, node: CompareExpr):
    # def visit_slice_argument(self, node: SliceArgument):
    # def visit_slice(self, node: Slice):
    # def visit_loop_statement(self, node: LoopStatement):    def visit_for(self, node: For):    def visit_while(self, node: While):
    # def visit_if(self, node: If):