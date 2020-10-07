from ply import lex

reserved = {word: word.upper() for word in 'if then for while break continue return eye zeros ones print'.split()}


tokens = ['PLUS',  'MINUS',  'TIMES',  'DIVIDE',
          'PLUS_MAT', 'MINUS_MAT', 'TIMES_MAT', "DIVIDE_MAT",
          'INT', 'FLOAT', 'STRING', 'ID', 'COMMENT',
          'ASSIGN', 'MINUS_ASSIGN', 'PLUS_ASSIGN', 'TIMES_ASSIGN', 'DIVIDE_ASSIGN',
          'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
         # 'LPAREN',  'RPAREN', 'LBRACE', 'RBRACE', 'LBRACK', 'RBRACK',
          #'RANGE', "TRANS", 'COM', 'SEMCOL'
            ] + list(reserved.values())



# patterns
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'

t_PLUS_MAT    = r'\.\+'
t_MINUS_MAT   = r'\.-'
t_TIMES_MAT   = r'\.\*'
t_DIVIDE_MAT  = r'\./'

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

# t_LPAREN  = r'\('
# t_RPAREN  = r'\)'
# t_LBRACE = r'{'
# t_RBRACE = r'}'
# t_LBRACK = r'['
# t_RBRACK = r']'

# t_RANGE = r':'
# t_TRANS = r"'"
# t_COM = r','
# t_SEMCOL = r';'

t_STRING = r'".*"'

literals = "()[]{}:',;"

# ignored chars
t_ignore = '  \t'

# value extraction
def t_FLOAT(t):
    r'(\d*\.\d+)|(\d+\.\d*)'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t) :
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_COMMENT(t):
    r'\#.*'
    pass

lexer = lex.lex()