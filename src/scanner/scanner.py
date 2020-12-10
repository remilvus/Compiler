from ply import lex

reserved = {word: word.upper() for word in 'if else for while break continue return eye zeros ones print'.split()}


tokens = ['PLUS',  'MINUS',  'TIMES',  'DIVIDE',
          'PLUS_MAT', 'MINUS_MAT', 'TIMES_MAT', "DIVIDE_MAT", "TRANSPOSE",
          'ASSIGN', 'MINUS_ASSIGN', 'PLUS_ASSIGN', 'TIMES_ASSIGN', 'DIVIDE_ASSIGN',
          'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
          'FLOAT', 'INT', 'STRING', 'ID'
          ] + list(reserved.values())


# operators
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

t_PLUS_MAT = r'\.\+'
t_MINUS_MAT = r'\.-'
t_TIMES_MAT = r'\.\*'
t_DIVIDE_MAT = r'\./'
t_TRANSPOSE = r"'"

t_ASSIGN = r'='
t_MINUS_ASSIGN = r'-='
t_PLUS_ASSIGN = r'\+='
t_TIMES_ASSIGN = r'\*='
t_DIVIDE_ASSIGN = r'/='

t_EQ = r'=='
t_NE = r'!='
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='


literals = "()[]{}:',;"


# value extraction
def t_FLOAT(t):
    r'((\d*\.\d+)|(\d+\.))(E[-+]?\d+)?'
    t.value = float(t.value)
    return t


def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'"([^"\\]|(\\")|(\\\\))*"'
    t.value = t.value[1:-1]
    t.value = t.value.replace(r'\"', r'"').replace('\\\\', '\\')
    return t


# variables
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')    # Check for reserved words
    return t


# comments
t_ignore_COMMENT = r'\#.*'


# whitespace characters
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' \t'


# error handling
def t_error(t):
    print(f"Illegal character '{t.value}', {position(t)}")
    t.lexer.skip(len(t.value))


# auxiliary functions
def find_column(input_text, token_lexpos):
    line_start = input_text.rfind('\n', 0, token_lexpos) + 1
    return (token_lexpos - line_start) + 1


def position(token):
    return f"line {token.lexer.lineno}, column {find_column(token.lexer.lexdata, token.lexer.lexpos)}"


lexer = lex.lex()
