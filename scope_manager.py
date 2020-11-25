class VariableSymbol():

    def __init__(self, name, type):
        pass


class SymbolTable(object):

    def __init__(self, parent, name): # parent scope and symbol table name
        self.scopes = [{}]

    def put(self, name, symbol): # put variable symbol or fundef under <name> entry
        self.scopes[-1][name] = symbol


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