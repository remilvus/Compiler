from enum import Enum, auto


class Type(Enum):
    INTNUM = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    RANGE = auto()
    VECTOR = auto()
    MATRIX = auto()
    NULL = auto()
    UNKNOWN = auto()

    @staticmethod
    def get_type(obj):
        obj_type = type(obj)
        if obj_type is int:
            return Type.INTNUM
        if obj_type is float:
            return Type.FLOAT
        if obj_type is str:
            return Type.STRING
        return Type.UNKNOWN
