import ply.yacc as yacc
from scanner import tokens



def p_term(p):
    'term : INT'
    p[0] = p[1]


def p_binary_operators(p):
    '''term : term PLUS term
                  | term MINUS term
                  | term '' term
                  | term '/' term'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]


parser = yacc.yacc()

while True:
    try:
        s = input()
    except EOFError:
        break
    if not s: continue
    result = parser.parse(s)
    print(result)
