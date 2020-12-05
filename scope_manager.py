from variables_types import Type


class Symbol:
    name = None
    type = None


class VariableSymbol(Symbol):
    def __init__(self, name, symbol_type):
        self.name = name
        self.type = symbol_type


# TODO I think we do not need VectorSymbol and MatrixSymbol // Samuel
class VectorSymbol(Symbol):
    def __init__(self, name, size):
        self.name = name
        self.type = Type.VECTOR
        self.size = size


class MatrixSymbol(Symbol):
    def __init__(self, name, width, height):
        self.name = name
        self.type = Type.MATRIX
        self.width = width
        self.height = height


# TODO currently (I think) all we need from here is checking whether we are in the loop
class SymbolTable(object):
    def __init__(self):
        self.scopes = []

    def put(self, name, symbol):  # put variable symbol or fundef under <name> entry
        self.scopes[-1][1][name] = symbol

    def check_exists(self, name):
        for _, scope in self.scopes[::-1]:
            if name in scope:
                return True
        return False

    def get(self, name):  # get variable symbol or fundef from <name> entry
        for _, scope in self.scopes[::-1]:
            if name in scope:
                return scope[name]

        return None

    def push_scope(self, name):
        self.scopes.append((name, {}))

    def pop_scope(self):
        self.scopes.pop()

    def is_loop(self):
        for name, _ in self.scopes:
            if name in {"while", "for"}:
                return True

        return False
