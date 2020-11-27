from ast import *
from scope_manager import *
from types import Type


class NodeVisitor(object):

    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node : Node):
       for child in node.children:
           self.visit(child)


class TypeChecker(NodeVisitor):
    # starting point
    def visit_Program(self, node : Program):
        self.visit(node.statements_list)

    # basic types
    def visit_Number(self, node : Number) -> Type:
        if type(node.number) is int:
            return Type.INTNUM
        elif type(node.number) is float:
            return Type.FLOAT

        raise AttributeError("Number with impossible type")

    def visit_Expression(self, node : Expression) -> Type:
        child = node.expression
        if type(child) is node:
            return self.visit(child)

        if Type.get_type(child) == Type.STRING: # only STRING goes straight to 'expression'
            return  Type.STRING

        raise AttributeError("Expression with impossible type")

    def visit_InnerVector(self, node : InnerVector) -> Type:



    def visit_Vector(self, node : Vector) -> Type:
    def visit_Matrix(self, node : Matrix) -> Type:

    # Arithmetic
    def visit_UnaryMinus(self, node: UnaryMinus) -> Type:

    def visit_BinExpr(self, node : BinExpr) -> Type:
        # alternative usage,
        # requires definition of accept method in class Node
        l_type = self.visit(node.left)  # type1 = node.left.accept(self)
        r_type = self.visit(node.right)  # type2 = node.right.accept(self)
        op = node.op

        if l_type == r_type:
            return l_type

        if (l_type, r_type) in {(Type.INTNUM, Type.FLOAT), (Type.FLOAT, Type.INTNUM)}:
            return Type.FLOAT

        # todo error handling

    def visit_MatrixBinExpr(self, node: MatrixBinExpr) -> Type:
        pass

    # Assigment
    def visit_AssignExpr(self, node: AssignExpr) -> Type:

    # Transposition
    def visit_Transposition(self, node: Transposition) -> Type:

    # Comparison
    def visit_CompareExpr(self, node: CompareExpr) -> Type:

    # slice & id
    def visit_SliceOrID(self, node : SliceOrID):
        if type(node) is str:
            var_name = node

            if self.symbol_table.check_exists(node):
                symbol = self.symbol_table.get(node)
                return symbol.type
            else:
                # variable may be on the right side of assigment
                return None
        # node is of type Slice
        assert type(node) is Slice
        return self.visit(node.slice_or_id)

    def visit_SliceArgument(self, node: SliceArgument) -> Type:
        pass

    def visit_Slice(self, node : Slice):
        symbol = self.symbol_table.get(node.identifier)
        if symbol.type != Type.VECOTR:
            pass
            # todo process error
        return Type.VECOTR

    # Flow control
    def visit_StatementsList(self, node: StatementsList) -> Type:
    def visit_CodeBlock(self, node : CodeBlock) -> Type:
    def visit_LoopStatement(self, node : LoopStatement) -> Type:
    def visit_For(self, node : For) -> Type:
    def visit_While(self, node : While) -> Type:
    def visit_If(self, node : If) -> Type:

    # def visit_Empty(self, node : Empty) -> Type:
    def visit_Range(self, node : Range) -> Type:

    def visit_Return(self, node : Return) -> Type:

    def visit_Print(self, node : Print) -> Type: