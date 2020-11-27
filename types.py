from enum import Enum, auto

class Type(Enum):
    INTNUM = auto()
    FLOAT = auto()
    STRING = auto()
    VECOTR = auto()
    MATRIX = auto()
    NULL = auto() # currently unused

    @staticmethod
    def get_type(object):
        obj_type = type(object)
        if obj_type is int:
            return Type.INTNUM
        if obj_type is float:
            return Type.FLOAT
        if obj_type is int:
            return Type.STRING
        return Type.NULL
