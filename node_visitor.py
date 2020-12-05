from ast import *
from scope_manager import *
from variables_types import Type


class NodeVisitor(object):
    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node):
        for child in node.children:
            if child:
                self.visit(child)


class TypeChecker(NodeVisitor):
    def visit_Program(self, node: Program):
        self.symbol_table.push_scope("program")
        self.visit(node.statements_list)
        self.symbol_table.pop_scope()

    def visit_Empty(self, node: Empty):
        pass

    @staticmethod
    def visit_Number(node: Number):
        node.type = Type.get_type(node.number)

    def visit_Expression(self, node: Expression):
        if Type.get_type(node.expression) == Type.STRING:
            node.type = Type.STRING
        else:
            self.visit(node.expression)
            node.type = node.expression.type
            node.size = node.expression.size

    def visit_InnerVector(self, node: InnerVector):
        types = []
        for element in node.inner_vector:
            self.visit(element)
            types.append(element.type)

        vector_type = Type.UNKNOWN
        for t in types:
            if t != Type.UNKNOWN:
                if vector_type == Type.UNKNOWN:
                    vector_type = t
                elif vector_type != t:
                    error(f"Vector elements should be of the same type. Found types: {vector_type} and {t}, " +
                          f"{node.position}")

        node.type = vector_type

        # when vector is a matrix
        if vector_type == Type.VECTOR:
            # rows sizes
            row_size = None
            for vector in node.inner_vector:
                if vector.type == Type.VECTOR:
                    if not row_size:
                        row_size = vector.size
                    elif row_size != vector.size:
                        error("Matrix has rows with different sizes. " +
                              f"Row {node.inner_vector.index(vector)} has size {vector.size} " +
                              f"while previous rows have size {row_size}, {vector.position}")

            node.size = (len(node.inner_vector), row_size)

            # rows types
            row_types = []
            for element in node.inner_vector:
                row_types.append(element.inner_vector.type)

                row_type = Type.UNKNOWN
                for t in row_types:
                    if t != Type.UNKNOWN:
                        if row_type == Type.UNKNOWN:
                            row_type = t
                        elif row_type != t:
                            error(f"Matrix elements should be of the same type. Found types: {row_type} and {t}, " +
                                  f"{node.position}")

        else:
            node.size = len(node.inner_vector)

    def visit_Vector(self, node: Vector):
        self.visit(node.inner_vector)

        if node.inner_vector.type == Type.VECTOR:
            node.type = Type.MATRIX
        else:
            node.type = Type.VECTOR

        node.size = node.inner_vector.size

    def visit_Matrix(self, node: Matrix):
        self.visit(node.argument)

        if node.argument.type not in {Type.INTNUM, Type.UNKNOWN}:
            error(f"Size of '{node.matrix_type}' matrix should be an integer. Found: {node.argument.type}, " +
                  f"{node.position}")

        node.type = Type.MATRIX

        if type(node.argument) == Expression and type(node.argument.expression) == Number:
            size = node.argument.expression.number
            node.size = (size, size)

    def visit_Range(self, node: Range):
        self.generic_visit(node)

        range_types = {Type.INTNUM, Type.UNKNOWN}
        if node.from_index.type not in range_types or node.to_index.type not in range_types:
            error(f"Range should contain only integers. Found: {node.from_index.type} and {node.to_index.type}, " +
                  f"{node.position}")

        node.type = Type.RANGE

    def visit_UnaryMinus(self, node: UnaryMinus):
        self.visit(node.value)

        if node.value.type not in {Type.INTNUM, Type.FLOAT, Type.UNKNOWN}:
            error(f"Negation is possible only for numbers. Found: {node.value.type}, {node.value.position}")
            node.type = Type.UNKNOWN
        else:
            node.type = node.value.type

    def visit_BinExpr(self, node: BinExpr):
        self.generic_visit(node)

        if node.left.type == Type.UNKNOWN or node.right.type == Type.UNKNOWN:
            node.type = Type.UNKNOWN
        elif node.left.type == node.right.type:
            node.type = node.left.type
        elif (node.left.type, node.right.type) in {(Type.INTNUM, Type.FLOAT), (Type.FLOAT, Type.INTNUM)}:
            node.type = Type.FLOAT
        else:
            error(f"Invalid types in binary expression. Left type: {node.left.type}, right type: {node.right.type}, " +
                  f"{node.position}")
            node.type = Type.UNKNOWN

    def visit_MatrixBinExpr(self, node: MatrixBinExpr):
        self.generic_visit(node)

        possible_type = {Type.MATRIX, Type.VECTOR, Type.UNKNOWN}
        if node.left.type not in possible_type or node.right.type not in possible_type:
            error(f"Matrix binary operations can be made only on matrices and vectors. Found {node.left.type} and " +
                  f"{node.right.type}, {node.position}")
            node.type = Type.UNKNOWN
        else:
            node.type = node.left.type if node.left.type != Type.UNKNOWN else node.right.type

        if node.left.size and node.right.size:
            if node.left.size == node.right.size:
                node.size = node.left.size
            else:
                error(f"Incompatible sizes within operation: '{node.operator}'. Found: {node.left.size} and " +
                      f"{node.right.size}, but they should be equal, {node.position}")

    def visit_Transposition(self, node: Transposition):
        self.visit(node.matrix)

        if node.matrix.type not in {Type.MATRIX, Type.UNKNOWN}:
            error(f"Only matrix can be transposed. Found: {node.matrix.type}, {node.position}")
        elif node.matrix.size:
            node.size = (node.matrix.size[1], node.matrix.size[0])

        node.type = Type.MATRIX

    def visit_CompareExpr(self, node: CompareExpr):
        self.generic_visit(node)
        node.type = Type.BOOLEAN

    def visit_SliceArgument(self, node: SliceArgument):
        self.visit(node.argument)
        if node.argument.type not in {Type.INTNUM, Type.RANGE, Type.UNKNOWN}:
            error(f"Slice argument have to be an integer of range. Found: {node.argument.type}, " +
                  f"{node.argument.position}")

        node.type = node.argument.type

    # TODO check slicing errors
    #  code below is assuming that type of variables cannot change what is a wrong assumption
    def visit_Slice(self, node: Slice):
        self.generic_visit(node)

        if not self.symbol_table.check_exists(node.identifier):
            self.symbol_table.put(node.identifier, VariableSymbol(node.identifier, Type.UNKNOWN))

        symbol = self.symbol_table.get(node.identifier)
        if symbol.type not in {Type.VECTOR, Type.MATRIX, Type.STRING, Type.UNKNOWN}:
            error(f"Slicing can be made only on vectors, matrices or strings. Found: {symbol.type}, {node.position}")

        if symbol.type in {Type.STRING, Type.UNKNOWN}:
            node.type = symbol.type
        elif node.slice_argument_1.type == Type.RANGE:
            if node.slice_argument_2 and node.slice_argument_2.type == Type.RANGE:
                node.type = Type.MATRIX
            else:
                node.type = Type.VECTOR
        elif node.slice_argument_2 and node.slice_argument_2.type == Type.RANGE:
            node.type = Type.VECTOR
        else:
            # can be either vector or matrix
            if symbol.type == Type.VECTOR:
                node.type = symbol.inner_vector.type
            else:
                # this can be made easier if we add Matrix and InnerMatrix to parser and ast
                node.type = symbol.inner_vector.inner_vector[0].inner_vector.type

    def visit_SliceOrID(self, node: SliceOrID):
        if type(node.slice_or_id) is str:
            if self.symbol_table.check_exists(node.slice_or_id):
                symbol = self.symbol_table.get(node.slice_or_id)
                node.type = symbol.type
            else:
                node.type = Type.UNKNOWN
                self.symbol_table.put(node.slice_or_id, VariableSymbol(node.slice_or_id, Type.UNKNOWN))
        else:
            self.visit(node.slice_or_id)

    def visit_AssignExpr(self, node: AssignExpr):
        self.generic_visit(node)
        node.type = Type.NULL

    def visit_StatementsList(self, node: StatementsList):
        for statement in node.statements_list:
            self.visit(statement)
        node.type = Type.NULL

    def visit_Return(self, node: Return):
        if node.value:
            self.visit(node.value)

        node.type = Type.NULL

    def visit_CodeBlock(self, node: CodeBlock):
        self.visit(node.statements_list)
        node.type = Type.NULL

    def visit_LoopStatement(self, node: LoopStatement):
        node.type = Type.NULL
        if not self.symbol_table.is_loop():
            error(f"Statement '{node.instruction}' should be in a loop, {node.position}")

    def visit_For(self, node: For):
        self.symbol_table.push_scope("for")
        self.symbol_table.put(node.iterator, VariableSymbol(node.iterator, Type.INTNUM))
        self.generic_visit(node)
        self.symbol_table.pop_scope()

        node.type = Type.NULL

    def visit_While(self, node: While):
        self.symbol_table.push_scope("while")
        self.generic_visit(node)
        self.symbol_table.pop_scope()

        if node.condition.type is not Type.BOOLEAN:
            error(f"Loop condition should be a boolean value, {node.condition.position}")

        node.type = Type.NULL

    def visit_If(self, node: If):
        self.symbol_table.push_scope("if")
        self.generic_visit(node)
        self.symbol_table.pop_scope()

        if node.condition.type is not Type.BOOLEAN:
            error(f"If condition should be a boolean value, {node.condition.position}")

        node.type = Type.NULL

    def visit_Print(self, node: Print):
        self.visit(node.value)
        node.type = Type.NULL


def error(message):
    print(message)
