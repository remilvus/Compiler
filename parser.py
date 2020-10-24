import ply.yacc as yacc
from scanner import *


precedence = (
    ('nonassoc', 'RANGE'),
    ('nonassoc', 'JUST_IF'),
    ('nonassoc', 'ELSE'),
    ('nonassoc', 'ASSIGN', 'MINUS_ASSIGN', 'PLUS_ASSIGN', 'TIMES_ASSIGN', 'DIVIDE_ASSIGN'),
    ('left', 'EQ','NE', 'GT', 'GE', 'LT', 'LE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'PLUS_MAT', 'MINUS_MAT'),
    ('left', 'TIMES_MAT', 'DIVIDE_MAT')
)


def p_number(p):
    """number : INT
              | FLOAT"""


def p_expression(p):
    """expression : ID
                  | number
                  | STRING
                  | matrix"""


def p_vector(p):
    """inner_vector : expression ',' expression
                    | inner_vector ',' expression
        vector      : '[' expression ']'
                    | '[' inner_vector ']' """


def p_matrix(p):
    """inner_matrix : vector
                    | inner_matrix ',' vector
       matrix       : '[' inner_matrix ']' """

def p_matrix(p):
    """inner_matrix : vector
                    | inner_matrix ',' vector
       matrix       : '[' inner_matrix ']' """


def p_matrix_maker(p):
    """matrix : ZEROS
              | EYE
              | ONES"""


def p_range(p):
    """range : INT ':' INT %prec RANGE"""


def p_binary_operators(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression"""

def p_matrix_binary_operators(p):
    """expression : expression PLUS_MAT expression
                  | expression MINUS_MAT expression
                  | expression TIMES_MAT expression
                  | expression DIVIDE_MAT expression"""

def p_negation(p):
    """expression : MINUS expression"""


def p_compare_equal(p):
    """expression : expression EQ expression
                  | expression NE expression"""


def p_compare_greater(p):
    """expression : expression GT expression
                  | expression GE expression"""


def p_compare_lower(p):
    """expression : expression LT expression
                  | expression LE expression"""


def p_statement(p):
    """statement : ID ASSIGN expression ';'
                 | ID MINUS_ASSIGN expression ';'
                 | ID PLUS_ASSIGN expression ';'
                 | ID TIMES_ASSIGN expression ';'
                 | ID DIVIDE_ASSIGN expression ';' """


def p_code_block(p):
    """code_block      : '{' statements_list '}'
                       | '{' statement '}'
       statements_list : statements_list statement
                       | statement statement"""


def p_loop(p):
    """statement : FOR ID EQ range code_block
                 | FOR ID EQ range statement
                 | WHILE '(' expression ')' code_block
                 | WHILE '(' expression ')' statement"""
    # reevaluating expression can be problematic



def p_if_statement(p):
    """statement : IF '(' expression ')' statement %prec JUST_IF
                 | IF '(' expression ')' code_block %prec JUST_IF
                 | IF '(' expression ')' statement else_block
                 | IF '(' expression ')' code_block else_block
       else_block : ELSE statement
                  | ELSE code_block"""

def p_print(p):
    """statement : PRINT inner_vector ';'"""


def p_error(p):
    if p:
        print("Syntax error at line {0}, column {1}: LexToken({2}, '{3}')"
              .format(p.lineno, find_column(p.lexer.lexdata, p.lexer.lexpos), p.type, p.value))
    else:
        print("Unexpected end of input")


parser = yacc.yacc(start='statements_list')
