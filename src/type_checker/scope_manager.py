from src.type_checker.variables_types import Type


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


class SymbolTable(object):
    def __init__(self):
        self.scopes = []
        self.loop_count = 0

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
        return self._find(name) is not None

    def get(self, name):  # get variable symbol or fundef from <name> entry
        for _, scope in self.scopes[::-1]:
            if name in scope:
                return scope[name]

        return None

    def push_scope(self, name):
        if name in {"while", "for"}:
            self.loop_count += 1
        self.scopes.append((name, {}))

    def pop_scope(self):
        name, _ = self.scopes.pop()
        if name in {"while", "for"}:
            self.loop_count -= 1

    def is_loop(self):
        return self.loop_count > 0

    def is_conditional(self):
        for name, _ in self.scopes:
            if name in {"while", "if"}:
                return True

        return False
