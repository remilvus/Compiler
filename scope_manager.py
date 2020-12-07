from variables_types import Type


class Symbol:
    name = None
    type = None


class VariableSymbol(Symbol):
    def __init__(self, name, symbol_type):
        self.name = name
        self.type = symbol_type


class VectorSymbol(Symbol):
    def __init__(self, name, size):
        self.name = name
        self.type = Type.VECTOR
        self.size = size

    def is_in(self, idx):
        return idx < self.size

class MatrixSymbol(Symbol):
    def __init__(self, name, height, width):
        self.name = name
        self.type = Type.MATRIX
        self.width = width
        self.height = height

    def is_in(self, height_idx, width_idx):
        return width_idx < self.width and height_idx < self.height


# TODO currently (I think) all we need from here is checking whether we are in the loop
class SymbolTable(object):
    def __init__(self):
        self.scopes = []

    def put(self, name, symbol):  # put variable symbol or fundef under <name> entry
        scope = self._find(name)
        if scope:
            scope[name] = symbol
        else:
            self.scopes[-1][1][name] = symbol

    def _find(self, name):
        for _, scope in self.scopes[::-1]:
            if name in scope:
                return scope
        return None

    def check_exists(self, name):
        return self._find(name) != None

    def get(self, name) -> Symbol:  # get variable symbol or fundef from <name> entry
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

    def is_conditional(self):
        for name, _ in self.scopes:
            if name in {"while", "if"}:
                return True

        return False
