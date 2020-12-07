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

        node.type = vector_type # possible type
        # this field says that there are instances of `vector_type`
        # but there can also be instances of `Type.UNKNOWN`

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
        assert node.size

    def visit_Matrix(self, node: Matrix):
        self.visit(node.argument)

        if node.argument.type not in {Type.INTNUM, Type.UNKNOWN}:
            error(f"Size of '{node.matrix_type}' matrix should be an integer. Found: {node.argument.type}, " +
                  f"{node.position}")


        if type(node.argument) == Expression and type(node.argument.expression) == Number:
            size = node.argument.expression.number
            node.size = (size, size)
            node.type = Type.MATRIX
        else:
            node.type = Type.UNKNOWN

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

        if self._is_null(node, node.left) or self._is_null(node, node.right):
            return

        bad_types = {Type.MATRIX, Type.VECTOR}
        if node.left.type in bad_types or node.right.type in bad_types:
            error(f"Invalid types in binary expression. Left type: {node.left.type}, right type: {node.right.type}, " +
                 f"{node.position}")
            node.type = Type.UNKNOWN
            return

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

        if self._is_null(node, node.left) or self._is_null(node, node.right):
            return

        possible_type = {Type.MATRIX, Type.VECTOR, Type.UNKNOWN}
        if node.left.type not in possible_type or node.right.type not in possible_type:
            error(f"Matrix binary operations can be made only on matrices and vectors. Found {node.left.type} and " +
                  f"{node.right.type}, {node.position}")
            node.type = Type.UNKNOWN
        else:
            if node.left.type == node.right.type:
                node.type = node.left.type
                node.size = node.left.size
            else:
                node.type = Type.UNKNOWN

        if node.left.size and node.right.size:
            if node.left.size == node.right.size:
                node.size = node.left.size
            else:
                error(f"Incompatible sizes within operation: '{node.operator}'. Found: {node.left.size} and " +
                      f"{node.right.size}, but they should be equal, {node.position}")
                node.type = Type.UNKNOWN
        if node.type in {Type.MATRIX, Type.VECTOR}:
            assert node.size

    def _is_null(self, node, var):
        if var.type == Type.NULL:
            error(f"Uninitialized variable used. " + f"{node.position}")
            node.type = Type.UNKNOWN
            return True
        return False

    def visit_Transposition(self, node: Transposition):
        self.visit(node.matrix)

        if node.matrix.type not in {Type.MATRIX, Type.UNKNOWN}:
            error(f"Only matrix can be transposed. Found: {node.matrix.type}, {node.position}")
            node.type = Type.UNKNOWN
        elif node.matrix.size:
            node.size = (node.matrix.size[1], node.matrix.size[0])
            node.type = Type.MATRIX

    def visit_CompareExpr(self, node: CompareExpr):
        self.generic_visit(node)

        if self._is_null(node, node.left) or self._is_null(node, node.right):
            return

        if Type.UNKNOWN in {node.left.type, node.right.type} or \
                node.left.type == node.right.type or \
                ({node.left.type, node.right.type} - {Type.INTNUM, Type.FLOAT}) == set():
            node.type = Type.BOOLEAN
        else:
            error(f"Invalid types in compare expression. Left type: {node.left.type}, right type: {node.right.type}, " +
                  f"{node.position}")

    def visit_SliceArgument(self, node: SliceArgument):
        self.visit(node.argument)
        if node.argument.type not in {Type.INTNUM, Type.RANGE, Type.UNKNOWN}:
            error(f"Slice argument have to be an integer of range. Found: {node.argument.type}, " +
                  f"{node.argument.position}")

        node.type = node.argument.type


    def visit_Slice(self, node: Slice):
        self.generic_visit(node)

        if not self.symbol_table.check_exists(node.identifier):
            error(
                f"Only initialized variables can be sliced. Variable `{node.identifier}` is uninitialized")
            node.type = Type.UNKNOWN
            return

        symbol = self.symbol_table.get(node.identifier)
        if symbol.type not in {Type.VECTOR, Type.MATRIX, Type.STRING, Type.UNKNOWN}:
            error(f"Slicing can be made only on vectors, matrices or strings. Found: {symbol.type}, {node.position}")

        if symbol.type in {Type.STRING, Type.UNKNOWN}:
            node.type = symbol.type
            return

        if node.slice_argument_1 and node.slice_argument_2:
            # sliced element must be 2D (a Matrix)
            if symbol.type != Type.MATRIX:
                error(f"Matrix slicing used with wrong type. Found: {symbol.type}, {node.position}")
                return
            self._visit_matrix_in_slice_2d(node, symbol)
        else:
            if symbol.type == Type.MATRIX:
                self._visit_matrix_in_slice(node, symbol)
            else:
                self._visit_vector_in_slice(node, symbol)

        assert node.type not in {Type.VECTOR, Type.MATRIX} or node.size != None

    @staticmethod
    def _get_number_from_expression(expr):
        if type(expr.expression) is Number:
            return expr.expression.number
        return None

    @staticmethod
    def _get_indices_from_range(range: Range):
        # gets indices if it's simple
        from_idx = TypeChecker._get_number_from_expression(
            range.from_index)
        to_idx = TypeChecker._get_number_from_expression(
            range.to_index)
        if not from_idx or not to_idx:
            return None, None
        return from_idx, to_idx

    def _visit_matrix_in_slice(self, node, symbol : MatrixSymbol):
        if node.slice_argument_1.type == Type.RANGE:

            # gets indices if it's simple
            from_idx, to_idx = self._get_indices_from_range(node.slice_argument_1.argument)
            if not from_idx or not to_idx:
                node.type = Type.UNKNOWN
                return

            if not (symbol.is_in(from_idx, 0) and symbol.is_in(to_idx, 0)):
                error(f'Bad index {node.position}')
                node.type = Type.UNKNOWN
                return
            node.type = Type.MATRIX
            node.size = (to_idx - from_idx, symbol.width)
        elif node.slice_argument_1.type == Type.INTNUM:
            if type(node.slice_argument_1.argument) is Number:
                idx = node.slice_argument_1.argument.number
                if not symbol.is_in(idx, 0):
                    error(f'Bad index {node.position}')
                node.type = Type.VECTOR
                node.size = symbol.width
        else:
            node.type = Type.UNKNOWN

    def _visit_vector_in_slice(self, node, symbol : VectorSymbol):
        if node.slice_argument_1.type == Type.RANGE:
            from_idx, to_idx = self._get_indices_from_range(
                node.slice_argument_1.argument)
            if not from_idx or not to_idx:
                node.type = Type.UNKNOWN
                return

            if not (symbol.is_in(from_idx) and symbol.is_in(to_idx)):
                error(f'Bad index {node.position}')
                node.type = Type.UNKNOWN
                return
            node.type = Type.VECTOR
            node.size = to_idx - from_idx
        elif node.slice_argument_1.type == Type.INTNUM:
            if type(node.slice_argument_1.argument) is Number:
                idx = node.slice_argument_1.argument.number
                if not symbol.is_in(idx):
                    error(f'Bad index {node.position}')
                node.type = Type.UNKNOWN
        else:
            node.type = Type.UNKNOWN

    def _visit_matrix_in_slice_2d(self, node, symbol : MatrixSymbol):
        if node.slice_argument_1.type == Type.RANGE:
            # gets indices if it's simple
            from_idx1, to_idx1 = self._get_indices_from_range(
                node.slice_argument_1.argument)
            if not from_idx1 or not to_idx1:
                node.type = Type.UNKNOWN
                return

            if node.slice_argument_2.type == Type.RANGE:
                # gets indices if it's simple
                from_idx2, to_idx2 = self._get_indices_from_range(
                    node.slice_argument_2.argument)
                if not from_idx1 or not to_idx1:
                    node.type = Type.UNKNOWN
                    return

                if not (symbol.is_in(from_idx1, from_idx2) and symbol.is_in(to_idx1,
                                                                            to_idx2)):
                    error(f'Bad index {node.position}')
                    node.type = Type.UNKNOWN
                    return
                node.type = Type.MATRIX
                node.size = (to_idx1 - from_idx1, to_idx2 - from_idx1)
            elif node.slice_argument_2 == Type.INTNUM:
                if type(node.slice_argument_2.argument) is Number:
                    idx = node.slice_argument_2.argument.number
                    if not (symbol.is_in(from_idx1, idx) and symbol.is_in(to_idx1,
                                                   idx)):
                        error(f'Bad index {node.position}')
                        node.type = Type.UNKNOWN
                        return
                    node.type = Type.VECTOR
                    node.size = to_idx1 - from_idx1
                else:
                    node.type = Type.UNKNOWN
            else:
                node.type = Type.UNKNOWN
        elif node.slice_argument_1.type == Type.INTNUM:
            if type(node.slice_argument_1.argument) is Number:
                idx = node.slice_argument_1.argument.number

                if type(node.slice_argument_2.argument) is Range:
                    from_idx = node.slice_argument_1.argument.from_index
                    to_idx = node.slice_argument_1.argument.from_index

                    if not (symbol.is_in(idx, from_idx) and symbol.is_in(idx, to_idx)):
                        error(f'Bad index {node.position}')
                        node.type = Type.UNKNOWN
                        return

                    node.type = Type.VECTOR
                    node.size = to_idx - from_idx
                elif node.slice_argument_2.type == Type.INTNUM:
                    if type(node.slice_argument_2.argument) is Number:
                        idx2 = node.slice_argument_1.argument.number
                        if not symbol.is_in(idx, idx2):
                            error(f'Bad index {node.position}')
                    node.type = Type.UNKNOWN
                else:
                    node.type = Type.UNKNOWN
            else:
                node.type = Type.UNKNOWN
        else:
            node.type = Type.UNKNOWN

    def visit_SliceOrID(self, node: SliceOrID):
        if type(node.slice_or_id) is str:  # id
            if self.symbol_table.check_exists(node.slice_or_id):
                symbol = self.symbol_table.get(node.slice_or_id)
                node.type = symbol.type
                if node.type == Type.VECTOR:
                    node.size = symbol.size
                    assert node.size
                elif node.type == Type.MATRIX:
                    node.size = (symbol.height, symbol.width)
                    assert node.size
            else:
                node.type = Type.NULL # higher node will create variable
        else:
            # slice
            slice = node.slice_or_id
            self.visit(slice)
            node.type = slice.type
            node.size = slice.size

    def visit_AssignExpr(self, node: AssignExpr):
        self.generic_visit(node)
        node.type = Type.NULL  # this node is child of statement

        # test for uninitialized symbol
        if self._is_null(node, node.right):
            return

        if node.left.type == Type.NULL:  # new id
            if node.operator != "=":
                error(f"Binary operation on uninitialized variable. Variable name: `{node.left.slice_or_id}`" +
                    f"{node.position}")
                node.type = Type.UNKNOWN
                return

            size = node.right.size
            self._put_symbol(node.left.slice_or_id, node.right.type, size)

        elif type(node.left.slice_or_id) is str:  # old id
            left = self.symbol_table.get(node.left.slice_or_id)
            if node.operator == "=":
                if left.type != node.right.type and self.symbol_table.is_conditional():
                    self._put_symbol(node.left.slice_or_id, Type.UNKNOWN)
                else:
                    size = node.right.size
                    self._put_symbol(node.left.slice_or_id, node.right.type, size)
            else:
                # update symbol type
                bad_types = {Type.MATRIX, Type.VECTOR}
                if left.type in bad_types or node.right.type in bad_types:
                    error(
                        f"Invalid types in assign-binary expression. Left type: {left.type}, right type: {node.right.type}, " +
                        f"{node.position}")
                    node.type = Type.UNKNOWN
                    return

                if left.type == Type.UNKNOWN or node.right.type == Type.UNKNOWN:
                    left.type = Type.UNKNOWN
                elif left.type == node.right.type:
                    pass
                elif ({left.type, node.right.type} - {Type.FLOAT, Type.INTNUM}) == set():
                    left.type = Type.FLOAT
                else:
                    error(f"Invalid types in assign-binary expression. Left type: {left.type}, right type: {node.right.type}, " +
                        f"{node.position}")
                    left.type = Type.UNKNOWN
        else:
            assert type(node.left) is Slice

            node.type = node.left.type
            if node.type in {Type.MATRIX, Type.VECTOR}:
                node.size = node.left.size



    def _put_symbol(self, name, type, size=None):
        if type not in {Type.VECTOR, Type.MATRIX}:
            self.symbol_table.put(name, VariableSymbol(name, type))
        else:
            assert size, f"{name} {type}"
            if type == Type.VECTOR:
                self.symbol_table.put(name, VectorSymbol(name, size))
            else:
                self.symbol_table.put(name, MatrixSymbol(name,
                                                   size[0], size[1]))

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
        self.symbol_table.push_scope("for")  # not a real scope
        self.symbol_table.put(node.iterator, VariableSymbol(node.iterator, Type.INTNUM))
        self.generic_visit(node)
        self.symbol_table.pop_scope()

        node.type = Type.NULL

    def visit_While(self, node: While):
        self.symbol_table.push_scope("while")  # not a real scope
        self.generic_visit(node)
        self.symbol_table.pop_scope()

        if node.condition.type is not Type.BOOLEAN:
            error(f"Loop condition should be a boolean value, {node.condition.position}")

        node.type = Type.NULL

    def visit_If(self, node: If):
        self.symbol_table.push_scope("if")  # not a real scope
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
