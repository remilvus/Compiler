from src.ast.ast import *
from src.type_checker.scope_manager import *
from src.type_checker.variables_types import Type

valid_operations = {
    Type.INTNUM: {"-"},
    Type.FLOAT: {"-"},

    (Type.INTNUM, Type.INTNUM): {"+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">="},
    (Type.INTNUM, Type.FLOAT): {"+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">="},
    (Type.FLOAT, Type.INTNUM): {"+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">="},
    (Type.FLOAT, Type.FLOAT): {"+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">="},

    (Type.STRING, Type.STRING): {"+", "==", "!=", "<", "<=", ">", ">="},

    (Type.STRING, Type.INTNUM): {"*", "==", "!="},
    (Type.INTNUM, Type.STRING): {"*", "==", "!="},

    (Type.VECTOR, Type.VECTOR): {".+", ".-", ".*", "./"},

    (Type.MATRIX, Type.MATRIX): {"*", ".+", ".-", ".*", "./"},
}

possible_operations = {**valid_operations, **{
    Type.UNKNOWN: {"-"},

    (Type.INTNUM, Type.UNKNOWN): {"+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">="},
    (Type.UNKNOWN, Type.INTNUM): {"+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">="},
    (Type.FLOAT, Type.UNKNOWN): {"+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">="},
    (Type.UNKNOWN, Type.FLOAT): {"+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">="},

    (Type.STRING, Type.UNKNOWN): {"+", "==", "!=", "<", "<=", ">", ">="},
    (Type.UNKNOWN, Type.STRING): {"+", "==", "!=", "<", "<=", ">", ">="},

    (Type.VECTOR, Type.UNKNOWN): {".+", ".-", ".*", "./"},
    (Type.UNKNOWN, Type.VECTOR): {".+", ".-", ".*", "./"},

    (Type.MATRIX, Type.UNKNOWN): {"*", ".+", ".-", ".*", "./"},
    (Type.UNKNOWN, Type.MATRIX): {"*", ".+", ".-", ".*", "./"},

    (Type.UNKNOWN, Type.UNKNOWN): {"+", "-", "*", "/", ".+", ".-", ".*", "./", "==", "!=", "<", "<=", ">", ">="}
}}


class NodeVisitor:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit(self, node):
        method = 'visit' + to_snake_case(node.__class__.__name__)
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node):
        for child in node.children:
            if child:
                self.visit(child)


class TypeChecker(NodeVisitor):
    def __init__(self):
        super().__init__()
        self.correct = True

    def visit_program(self, node: Program):
        self.symbol_table.push_scope("program")
        self.visit(node.statements_list)
        self.symbol_table.pop_scope()

    def visit_empty(self, node: Empty):
        pass

    @staticmethod
    def visit_number(node: Number):
        node.type = Type.get_type(node.number)

    def visit_expression(self, node: Expression):
        if Type.get_type(node.expression) == Type.STRING:
            node.type = Type.STRING
        else:
            self.visit(node.expression)
            node.type = node.expression.type
            node.size = node.expression.size

    def visit_inner_vector(self, node: InnerVector):
        types = []
        for element in node.inner_vector:
            self.visit(element)
            self.__check_null(node, element)
            types.append(element.type)

        node._error_request = None
        vector_type = Type.UNKNOWN
        for t in types:
            if t != Type.UNKNOWN:
                if vector_type == Type.UNKNOWN:
                    vector_type = t
                elif vector_type != t:
                    node._error_request = f"Vector elements should be of the " + \
                                          f"same type. Found types: {vector_type} and {t}, " +\
                                          f"{node.position}"

        node.type = vector_type  # possible type
        # this field says that there are instances of `vector_type`
        # but there can also be instances of `Type.UNKNOWN`

        # when vector is a matrix
        if vector_type == Type.VECTOR and len(node.inner_vector) > 0 and type(node.inner_vector[0]) == Vector:
            # rows sizes
            row_size = None
            for vector in node.inner_vector:
                if vector.type == Type.VECTOR:
                    if not row_size:
                        row_size = vector.size
                    elif row_size != vector.size:
                        self._error("Matrix has rows with different sizes. " +
                                    f"Row {node.inner_vector.index(vector)} has size {vector.size} " +
                                    f"while previous rows have size {row_size}, {vector.position}")

            node.size = (len(node.inner_vector), row_size)

            # rows types
            row_types = []
            for element in node.inner_vector:
                if isinstance(element, Vector):
                    row_types.append(element.inner_vector.type)

            row_type = Type.UNKNOWN
            for t in row_types:
                if t != Type.UNKNOWN:
                    if row_type == Type.UNKNOWN:
                        row_type = t
                    elif row_type != t:
                        self._error(f"Matrix elements should be " +
                                    f"of the same type. Found types: {row_type} and {t}, " +
                                    f"{node.position}")

        elif vector_type == Type.VECTOR:
            node.type = Type.UNKNOWN
        else:
            node.size = len(node.inner_vector)

    def visit_vector(self, node: Vector):
        self.visit(node.inner_vector)
        if node.inner_vector._error_request:
            self._error(node.inner_vector._error_request)

        if node.inner_vector.type == Type.UNKNOWN:
            node.type = Type.UNKNOWN
        elif node.inner_vector.type == Type.VECTOR:
            node.type = Type.MATRIX
            node.size = node.inner_vector.size
        else:
            node.type = Type.VECTOR
            node.size = node.inner_vector.size

    def visit_matrix(self, node: Matrix):
        self.visit(node.argument)

        if node.argument.type not in {Type.INTNUM, Type.UNKNOWN}:
            self._error(f"Size of '{node.matrix_type}' matrix should be an integer. Found: {node.argument.type}, " +
                        f"{node.position}")

        if type(node.argument) == Expression and type(node.argument.expression) == Number:
            size = node.argument.expression.number
            node.size = (size, size)
            node.type = Type.MATRIX
        else:
            node.type = Type.UNKNOWN

    def visit_range(self, node: Range):
        self.generic_visit(node)

        range_types = {Type.INTNUM, Type.UNKNOWN}
        if node.from_index.type not in range_types or node.to_index.type not in range_types:
            self._error(f"Range should contain only integers. Found: {node.from_index.type} and {node.to_index.type}, " +
                        f"{node.position}")

        node.type = Type.RANGE

    def visit_unary_minus(self, node: UnaryMinus):
        self.visit(node.value)

        if not self.__check_null(node, node.value):
            if node.value.type in possible_operations and "-" in possible_operations[node.value.type]:
                node.type = node.value.type
            else:
                self._error(f"Negation is possible only for numbers. Found: {node.value.type}, {node.value.position}")
                node.type = Type.UNKNOWN

    def visit_bin_expr(self, node: BinExpr):
        self.generic_visit(node)

        if not self.__check_null(node, node.left) and not self.__check_null(node, node.right):
            expr_type = (node.left.type, node.right.type)

            if expr_type in possible_operations and node.operator in possible_operations[expr_type]:
                if node.left.type == Type.FLOAT or node.right.type == Type.FLOAT or node.operator == "/":
                    node.type = Type.FLOAT
                elif node.left.type == Type.STRING or node.right.type == Type.STRING:
                    node.type = Type.STRING
                else:
                    node.type = node.left.type if node.left.type != Type.UNKNOWN else node.right.type

                if node.type == Type.MATRIX:
                    if node.left.type == Type.UNKNOWN or node.right.type == Type.UNKNOWN:
                        node.type = Type.UNKNOWN
                    else:
                        self.__check_matrix_multiplication(node)
                        node.size = (node.left.size[0], node.right.size[1])
            else:
                node.type = Type.UNKNOWN
                self._error(f"Invalid types in binary expression. Left type: {node.left.type}, " +
                            f"right type: {node.right.type}, {node.position}")

    def __check_matrix_multiplication(self, node):
        if node.left.size[1] != node.right.size[0]:
            self._error(f"Incompatible matrices sizes in matrix multiplication. " +
                        f"Found {node.left.size} and {node.right.size}, {node.right.position}")

    def visit_matrix_bin_expr(self, node: MatrixBinExpr):
        self.generic_visit(node)

        if not self.__check_null(node, node.left) and not self.__check_null(node, node.right):
            expr_type = (node.left.type, node.right.type)

            if expr_type in possible_operations and node.operator in possible_operations[expr_type]:
                if expr_type[0] == Type.UNKNOWN or expr_type[1] == Type.UNKNOWN:
                    node.type = Type.UNKNOWN
                elif node.left.size == node.right.size:
                    node.type = node.left.type
                    node.size = node.left.size
                else:
                    node.type = Type.UNKNOWN
                    self._error(f"Incompatible sizes within operation: '{node.operator}'. Found: {node.left.size} and " +
                                f"{node.right.size}, but they should be equal, {node.position}")
            else:
                node.type = Type.UNKNOWN
                self._error("Matrix binary operations can be made only on matrices and vectors. " +
                            f"Found {node.left.type} and {node.right.type}, {node.position}")

    def __check_null(self, node, var):
        if var.type == Type.NULL:
            self._error(f"Uninitialized variable used, {node.position}")
            node.type = Type.UNKNOWN
            return True
        return False

    def visit_transposition(self, node: Transposition):
        self.visit(node.matrix)

        if node.matrix.type in {Type.MATRIX, Type.UNKNOWN}:
            if node.matrix.type == Type.MATRIX:
                node.size = (node.matrix.size[1], node.matrix.size[0])

            node.type = node.matrix.type
        else:
            self._error(f"Only matrix can be transposed. Found: {node.matrix.type}, {node.position}")
            node.type = Type.UNKNOWN

    def visit_compare_expr(self, node: CompareExpr):
        self.generic_visit(node)

        if not self.__check_null(node, node.left) and not self.__check_null(node, node.right):
            expr_type = (node.left.type, node.right.type)
            if expr_type not in possible_operations or node.operator not in possible_operations[expr_type]:
                self._error("Incompatible types for comparison. " +
                            f"Left type: {node.left.type}, right type: {node.right.type}, {node.position}")

        node.type = Type.BOOLEAN

    def visit_slice_argument(self, node: SliceArgument):
        self.visit(node.argument)
        if node.argument.type not in {Type.INTNUM, Type.RANGE, Type.UNKNOWN}:
            self._error(f"Slice argument have to be an integer or range. Found: {node.argument.type}, " +
                        f"{node.argument.position}")

        node.type = node.argument.type

    def visit_slice(self, node: Slice):
        self.generic_visit(node)

        if not self.symbol_table.check_exists(node.identifier):
            self._error(
                f"Only initialized variables can be sliced. Variable `{node.identifier}` is uninitialized")
            node.type = Type.UNKNOWN
            return

        symbol = self.symbol_table.get(node.identifier)
        if symbol.type not in {Type.VECTOR, Type.MATRIX, Type.STRING, Type.UNKNOWN}:
            self._error(f"Slicing can be made only on vectors, matrices or strings. Found: {symbol.type}, {node.position}")

        if symbol.type in {Type.STRING, Type.UNKNOWN}:
            node.type = symbol.type
            return

        if node.slice_argument_1 and node.slice_argument_2:
            # sliced element must be 2D (a Matrix)
            if symbol.type != Type.MATRIX:
                self._error(f"Matrix slicing used with wrong type. Found: {symbol.type}, {node.position}")
                return
            self._visit_matrix_in_slice_2d(node, symbol)
        else:
            if symbol.type == Type.MATRIX:
                self._visit_matrix_in_slice(node, symbol)
            else:
                self._visit_vector_in_slice(node, symbol)

        assert node.type not in {Type.VECTOR, Type.MATRIX} or node.size is not None

    @staticmethod
    def _get_number_from_expression(expr):
        if type(expr) is UnaryMinus and type(expr.value.expression) is Number:
            return -expr.value.expression.number
        elif type(expr.expression) is Number:
            return expr.expression.number
        return None

    @staticmethod
    def _get_indices_from_range(slice_range: Range):
        # gets indices if it's simple
        from_idx = TypeChecker._get_number_from_expression(slice_range.from_index)
        to_idx = TypeChecker._get_number_from_expression(slice_range.to_index)

        return (from_idx, to_idx) if (from_idx is not None and to_idx is not None) else (None, None)

    def _visit_matrix_in_slice(self, node, symbol: MatrixSymbol):
        if node.slice_argument_1.type == Type.RANGE:

            # gets indices if it's simple
            from_idx, to_idx = self._get_indices_from_range(node.slice_argument_1.argument)
            if from_idx is None or to_idx is None:
                node.type = Type.UNKNOWN
                return

            if not (symbol.is_in(from_idx, 0, is_range=True) and symbol.is_in(to_idx, 0, is_range=True)):
                self._error(f'Bad index {node.position}')
                node.type = Type.UNKNOWN
                return
            node.type = Type.MATRIX
            node.size = (to_idx - from_idx, symbol.width)
        elif node.slice_argument_1.type == Type.INTNUM:
            if self._is_slice_argument_a_number(node.slice_argument_1):
                idx = self._get_number_from_slice_argument(node.slice_argument_1)
                if not symbol.is_in(idx, 0):
                    self._error(f'Bad index {node.position}')
                node.type = Type.VECTOR
                node.size = symbol.width
        else:
            node.type = Type.UNKNOWN

    def _visit_vector_in_slice(self, node, symbol: VectorSymbol):
        if node.slice_argument_1.type == Type.RANGE:
            from_idx, to_idx = self._get_indices_from_range(node.slice_argument_1.argument)
            if from_idx is None or to_idx is None:
                node.type = Type.UNKNOWN
                return

            if not (symbol.is_in(from_idx, is_range=True) and symbol.is_in(to_idx, is_range=True)):
                self._error(f'Bad index {node.position}')
                node.type = Type.UNKNOWN
                return
            node.type = Type.VECTOR
            node.size = to_idx - from_idx
        elif node.slice_argument_1.type == Type.INTNUM:
            if self._is_slice_argument_a_number(node.slice_argument_1):
                idx = self._get_number_from_slice_argument(node.slice_argument_1)
                if not symbol.is_in(idx):
                    self._error(f'Bad index {node.position}')
                node.type = Type.UNKNOWN
        else:
            node.type = Type.UNKNOWN

    def _visit_matrix_in_slice_2d(self, node, symbol: MatrixSymbol):
        if node.slice_argument_1.type == Type.RANGE:
            # gets indices if it's simple
            from_idx1, to_idx1 = self._get_indices_from_range(node.slice_argument_1.argument)
            if from_idx1 is None or to_idx1 is None:
                node.type = Type.UNKNOWN
                return

            if not (symbol.is_in(from_idx1, 0, is_range=True) and symbol.is_in(to_idx1, 0, is_range=True)):
                self._error(f'Bad index {node.position}')
                node.type = Type.UNKNOWN
                return

            if node.slice_argument_2.type == Type.RANGE:
                # gets indices if it's simple
                from_idx2, to_idx2 = self._get_indices_from_range(node.slice_argument_2.argument)
                if from_idx1 is None or to_idx1 is None:
                    node.type = Type.UNKNOWN
                    return

                if not (symbol.is_in(0, from_idx2, is_range=True) and symbol.is_in(0, to_idx2, is_range=True)):
                    self._error(f'Bad index {node.position}')
                    node.type = Type.UNKNOWN
                    return

                node.type = Type.MATRIX
                node.size = (to_idx1 - from_idx1, to_idx2 - from_idx1)
            elif node.slice_argument_2.type == Type.INTNUM:
                if self._is_slice_argument_a_number(node.slice_argument_2):
                    idx = self._get_number_from_slice_argument(node.slice_argument_2)
                    if not symbol.is_in(0, idx):
                        self._error(f'Bad index {node.position}')
                        node.type = Type.UNKNOWN
                        return
                    node.type = Type.VECTOR
                    node.size = to_idx1 - from_idx1
                else:
                    node.type = Type.UNKNOWN
            else:
                node.type = Type.UNKNOWN
        elif node.slice_argument_1.type == Type.INTNUM:
            if self._is_slice_argument_a_number(node.slice_argument_1):
                idx = self._get_number_from_slice_argument(node.slice_argument_1)

                if not symbol.is_in(idx, 0):
                    self._error(f'Bad index {node.position}')
                    node.type = Type.UNKNOWN
                    return

                if node.slice_argument_2.type == Type.RANGE:
                    from_idx, to_idx = self._get_indices_from_range(node.slice_argument_2.argument)

                    if not (symbol.is_in(0, from_idx, is_range=True) and symbol.is_in(0, to_idx, is_range=True)):
                        self._error(f'Bad index {node.position}')
                        node.type = Type.UNKNOWN
                        return

                    node.type = Type.VECTOR
                    node.size = to_idx - from_idx
                elif node.slice_argument_2.type == Type.INTNUM:
                    if self._is_slice_argument_a_number(node.slice_argument_2):
                        idx2 = self._get_number_from_slice_argument(node.slice_argument_2)
                        if not symbol.is_in(0, idx2):
                            self._error(f'Bad index {node.position}')
                    node.type = Type.UNKNOWN
                else:
                    node.type = Type.UNKNOWN
            else:
                node.type = Type.UNKNOWN
        else:
            node.type = Type.UNKNOWN

    @staticmethod
    def _is_slice_argument_a_number(slice_argument):
        if type(slice_argument.argument) is UnaryMinus and type(slice_argument.argument.value.expression) is Number:
            return True

        return type(slice_argument.argument) is Expression and type(slice_argument.argument.expression) is Number

    @staticmethod
    def _get_number_from_slice_argument(slice_argument):
        if type(slice_argument.argument) is UnaryMinus:
            return -slice_argument.argument.value.expression.number
        else:
            return slice_argument.argument.expression.number

    def visit_slice_or_id(self, node: SliceOrID):
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
                node.type = Type.NULL  # higher node will create variable
        else:
            # slice
            slice = node.slice_or_id
            self.visit(slice)
            node.type = slice.type
            node.size = slice.size

    def visit_assign_expr(self, node: AssignExpr):
        self.generic_visit(node)
        node.type = Type.NULL  # this node is child of statement

        # test for uninitialized symbol
        if self.__check_null(node, node.right):
            return

        if node.left.type == Type.NULL:  # new id
            if node.operator != "=":
                self._error(f"Binary operation on uninitialized variable. Variable name: `{node.left.slice_or_id}`, " +
                            f"{node.left.position}")
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
                    self._error(
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
                    self._error(f"Invalid types in assign-binary expression. Left type: {left.type}, right type: {node.right.type}, " +
                                f"{node.position}")
                    left.type = Type.UNKNOWN
        else:
            assert isinstance(node.left.slice_or_id, Slice)

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
                self.symbol_table.put(name, MatrixSymbol(name, size[0], size[1]))

    def visit_statements_list(self, node: StatementsList):
        for statement in node.statements_list:
            self.visit(statement)
        node.type = Type.NULL

    def visit_return(self, node: Return):
        if node.value:
            self.visit(node.value)

        node.type = Type.NULL

    def visit_code_block(self, node: CodeBlock):
        self.visit(node.statements_list)
        node.type = Type.NULL

    def visit_loop_statement(self, node: LoopStatement):
        node.type = Type.NULL
        if not self.symbol_table.is_loop():
            self._error(f"Statement '{node.instruction}' should be in a loop, {node.position}")

    def visit_for(self, node: For):
        self.symbol_table.push_scope("for")  # not a real scope
        self.symbol_table.put(node.iterator, VariableSymbol(node.iterator, Type.INTNUM))
        self.generic_visit(node)
        self.symbol_table.pop_scope()

        node.type = Type.NULL

    def visit_while(self, node: While):
        self.symbol_table.push_scope("while")  # not a real scope
        self.generic_visit(node)
        self.symbol_table.pop_scope()

        if node.condition.type is not Type.BOOLEAN:
            self._error(f"Loop condition should be a boolean value, {node.condition.position}")

        node.type = Type.NULL

    def visit_if(self, node: If):
        self.symbol_table.push_scope("if")  # not a real scope
        self.generic_visit(node)
        self.symbol_table.pop_scope()

        if node.condition.type is not Type.BOOLEAN:
            self._error(f"If condition should be a boolean value, {node.condition.position}")

        node.type = Type.NULL

    def visit_print(self, node: Print):
        self.visit(node.value)
        node.type = Type.NULL

    def _error(self, message):
        print(message)
        self.correct = False


def to_snake_case(name):
    snake_case_name = ""
    for i in range(len(name)):
        if name[i].isupper() and not name[i-1:i+1] == "ID":
            snake_case_name += f"_{name[i].lower()}"
        else:
            snake_case_name += name[i].lower()

    return snake_case_name
