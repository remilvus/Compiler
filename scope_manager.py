from types import Type


class Symbol():
    name = None
    type = None


class VariableSymbol(Symbol):
    def __init__(self, name, type):
        self.name = name
        self.type = type


class VectorSymbol(Symbol):
    def __init__(self, name, size):
        self.name = name
        self.type = Type.VECOTR
        self.size = size


class MatrixSymbol(Symbol):
    def __init__(self, name, width, height):
        self.name = name
        self.type = Type.MATRIX
        self.width = width
        self.height = height


class SymbolTable(object):
    def __init__(self, parent, name): # parent scope and symbol table name
        self.scopes = [{}]

    def put(self, name, symbol): # put variable symbol or fundef under <name> entry
        self.scopes[-1][name] = symbol

    def check_exists(self, name):
        for scope in self.scopes[::-1]:
            if name in scope:
                return True
        return False

    def get(self, name): # get variable symbol or fundef from <name> entry
        for scope in self.scopes[::-1]:
            if name in scope:
                return scope[name]
        # todo save error information

    # def getParentScope(self):
    #     pass
    # #

    def pushScope(self, name):
        self.scopes.append({})

    def popScope(self):
        self.scopes.pop()