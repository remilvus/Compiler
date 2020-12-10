import ply.yacc as yacc
from src.scanner.scanner import *
from src.ast.tree_printer import *

precedence = (
    ('nonassoc', 'JUST_IF'),
    ('nonassoc', 'ELSE'),
    ('nonassoc', 'ASSIGN', 'MINUS_ASSIGN', 'PLUS_ASSIGN', 'TIMES_ASSIGN', 'DIVIDE_ASSIGN'),
    ('left', 'EQ', 'NE', 'GT', 'GE', 'LT', 'LE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'NEGATION'),
    ('left', 'PLUS_MAT', 'MINUS_MAT'),
    ('left', 'TIMES_MAT', 'DIVIDE_MAT'),
    ('left', 'TRANSPOSE')
)


def p_program(p):
    """program : statements_list
               | empty"""

    p[0] = Program(position(p), p[1])


def p_empty(p):
    """empty :"""
    p[0] = Empty(position(p))


def p_number(p):
    """number : INT
              | FLOAT"""

    p[0] = Number(position(p), p[1])


def p_expression(p):
    """expression : slice_or_id
                  | number
                  | STRING"""
    p[0] = Expression(position(p), p[1])


def p_inner_vector(p):
    """inner_vector : inner_vector ',' expression
                    | expression"""

    if len(p) == 2:
        p[0] = InnerVector(position(p), [], p[1])
    else:
        p[0] = InnerVector(position(p), p[1], p[3])


def p_vector(p):
    """expression : '[' inner_vector ']' """
    p[0] = Vector(position(p), p[2])


def p_matrix_maker(p):
    """expression : ZEROS '(' expression ')'
                  | EYE '(' expression ')'
                  | ONES '(' expression ')' """

    p[0] = Matrix(position(p), p[1], p[3])

    
def p_range(p):
    """range : expression ':' expression"""
    p[0] = Range(position(p), p[1], p[3])


def p_negation(p):
    """expression : MINUS expression %prec NEGATION"""
    p[0] = UnaryMinus(position(p), p[2])


def p_binary_operators(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression"""

    p[0] = BinExpr(position(p), p[2], p[1], p[3])


def p_matrix_binary_operators(p):
    """expression : expression PLUS_MAT expression
                  | expression MINUS_MAT expression
                  | expression TIMES_MAT expression
                  | expression DIVIDE_MAT expression"""

    p[0] = MatrixBinExpr(position(p), p[2], p[1], p[3])


def p_transposition(p):
    """expression : expression TRANSPOSE"""
    p[0] = Transposition(position(p), p[1])


def p_compare(p):
    """expression : expression EQ expression
                  | expression NE expression
                  | expression GT expression
                  | expression GE expression
                  | expression LT expression
                  | expression LE expression"""

    p[0] = CompareExpr(position(p), p[2], p[1], p[3])


def p_slice_argument(p):
    """slice_argument : expression
                      | range"""

    p[0] = SliceArgument(position(p), p[1])


def p_slice(p):
    """slice : ID '[' slice_argument ']'
             | ID '[' slice_argument ',' slice_argument ']' """

    if len(p) == 5:
        p[0] = Slice(position(p), p[1], p[3], None)
    else:
        p[0] = Slice(position(p), p[1], p[3], p[5])


def p_slice_or_id(p):
    """slice_or_id : ID
                   | slice"""

    p[0] = SliceOrID(position(p), p[1])


def p_statement(p):
    """statement : slice_or_id ASSIGN expression ';'
                 | slice_or_id MINUS_ASSIGN expression ';'
                 | slice_or_id PLUS_ASSIGN expression ';'
                 | slice_or_id TIMES_ASSIGN expression ';'
                 | slice_or_id DIVIDE_ASSIGN expression ';' """

    p[0] = AssignExpr(position(p), p[2], p[1], p[3])


def p_statements_list(p):
    """statements_list : statements_list statement
                       | statement"""

    if len(p) == 2:
        p[0] = StatementsList(position(p), [], p[1])
    else:
        p[0] = StatementsList(position(p), p[1], p[2])


def p_return_statement(p):
    """statement : RETURN ';'
                 | RETURN expression ';' """

    if len(p) == 3:
        p[0] = Return(position(p), None)
    else:
        p[0] = Return(position(p), p[2])


def p_code_block(p):
    """statement : '{' statements_list '}' """
    p[0] = CodeBlock(position(p), p[2])


def p_loop_statement(p):
    """statement : BREAK ';'
                 | CONTINUE ';' """

    p[0] = LoopStatement(position(p), p[1])


def p_for_loop(p):
    """statement : FOR ID ASSIGN range statement"""
    p[0] = For(position(p), p[2], p[4], p[5])


def p_while_loop(p):
    """statement : WHILE '(' expression ')' statement"""
    p[0] = While(position(p), p[3], p[5])


def p_if_statement(p):
    """statement : IF '(' expression ')' statement %prec JUST_IF
                 | IF '(' expression ')' statement ELSE statement"""

    if len(p) == 6:
        p[0] = If(position(p), p[3], p[5], None)
    else:
        p[0] = If(position(p), p[3], p[5], p[7])


def p_print(p):
    """statement : PRINT inner_vector ';' """
    p[0] = Print(position(p), p[2])


def p_error(p):
    if p:
        print(f"Syntax error, {position(p)}, LexToken({p.type}, '{p.value}')")
    else:
        print("Unexpected end of input")


parser = yacc.yacc(start='program')
