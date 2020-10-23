import ply.yacc as yacc
from scanner import *


precedence = (
    ('nonassoc', 'JUST_IF'),
    ('left', 'EQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)


def p_number(p):
    '''number : INT
              | FLOAT'''


def p_expression(p):
    '''expression : ID
                  | number
                  | STRING'''


def p_vector(p):
    '''inner_vector : expression ',' expression
                    | inner_vector ',' expression
        vector      : '[' expression ']'
                    | '[' inner_vector ']' '''


def p_matrix(p):
    '''inner_matrix : vector
                    | inner_matrix ',' vector
       matrix       : '[' inner_matrix ']' '''


def p_plus(p):
    '''expression : expression PLUS expression'''


def p_equal(p):
    '''expression : expression EQ expression'''


def p_statement(p):
    '''statement : expression ';'
                 | '{' statement '}' '''


def p_if_statement(p):
    '''statement : IF '(' expression ')' statement %prec JUST_IF
                 | IF '(' expression ')' statement ELSE statement'''


def p_error(p):
    if p:
        print("Syntax error at line {0}, column {1}: LexToken({2}, '{3}')"
              .format(p.lineno, find_column(p.lexer.lexdata, p.lexer.lexpos), p.type, p.value))
    else:
        print("Unexpected end of input")


parser = yacc.yacc(start='statement')
