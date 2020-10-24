import ply.yacc as yacc
from scanner import *


precedence = (
    ('nonassoc', 'JUST_IF'),
    ('nonassoc', 'ELSE'),
    ('nonassoc', 'ASSIGN', 'MINUS_ASSIGN', 'PLUS_ASSIGN', 'TIMES_ASSIGN', 'DIVIDE_ASSIGN'),
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
    '''statement : ID ASSIGN expression ';'
                 | ID MINUS_ASSIGN expression ';'
                 | ID PLUS_ASSIGN expression ';'
                 | ID TIMES_ASSIGN expression ';'
                 | ID DIVIDE_ASSIGN expression ';' '''


def p_code_block(p):
    '''code_block      : '{' statements_list '}'
                       | '{' statement '}'
       statements_list : statements_list statement
                       | statement statement'''


def p_if_statement(p):
    '''statement : IF '(' expression ')' statement %prec JUST_IF
                 | IF '(' expression ')' code_block %prec JUST_IF
                 | IF '(' expression ')' statement else_block
                 | IF '(' expression ')' code_block else_block
       else_block : ELSE statement
                  | ELSE code_block'''


def p_error(p):
    if p:
        print("Syntax error at line {0}, column {1}: LexToken({2}, '{3}')"
              .format(p.lineno, find_column(p.lexer.lexdata, p.lexer.lexpos), p.type, p.value))
    else:
        print("Unexpected end of input")


parser = yacc.yacc(start='statements_list')
