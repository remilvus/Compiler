from enum import Enum, auto
import numpy as np


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
        if isinstance(obj, np.ndarray):
            if len(obj.shape) == 1:
                return Type.VECTOR
            else:
                return Type.MATRIX
        if obj_type is list:
            return Type.VECTOR
        return Type.UNKNOWN
