from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Memory:
    name: str
    symbols: Dict[str, Any] = field(default_factory=dict)

    def has_key(self, name):  # variable name
        return name in self.symbols

    def get(self, name):         # gets from memory current value of variable <name>

        return self.symbols[name]
    def put(self, name, value):  # puts into memory current value of variable <name>

        self.symbols[name] = value

@dataclass
class MemoryStack:
    stack: List[Memory] = field(default_factory=lambda: [Memory('global')])

    def get(self, name):             # gets from memory stack current value of variable <name>
        memory = self._find(name)
        if memory:
            return memory.get(name)
        else:
            raise KeyError(f'{name} not found')

    def set(self, name, value): # inserts into memory stack variable <name> with value <value>
        memory : Memory = self._find(name)
        if not memory:
            memory = self.stack[-1]

        memory.put(name, value)

    def push(self, name): # creates new memory and pushes it onto the stack
        self.stack.append(Memory(name=name))

    def pop(self):          # pops the top memory from the stack
        self.stack.pop()

    def _find(self, name): # finds first <memory> containing <name>
        for mem in self.stack[::-1]:
            if mem.has_key(name):
                return mem
        return None

