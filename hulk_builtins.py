from utils.semantic import Type
from utils.semantic import *

def get_builtin_types() -> list[Type]:
    return [ObjectType(), StringType(), NumberType(), BooleanType()]