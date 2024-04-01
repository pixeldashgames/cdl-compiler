from utils.semantic import Type
from utils.semantic import *

def get_builtin_types() -> list[Type]:
    return [ObjectType(), StringType(), NumberType(), BooleanType(), IterableType()]

def get_builtin_functions() -> list[tuple[str, list[str], list[Type], Type]]:
    return [
        ("sqrt", ["x"], [NumberType()], [NumberType()]),
        ("sin", ["x"], [NumberType()], [NumberType()]),
        ("cos", ["x"], [NumberType()], [NumberType()]),
        ("exp", ["x"], [NumberType()], [NumberType()]),
        ("log", ["b", "x"], [NumberType(), NumberType()], [NumberType()]),
        ("rand", [], [], [NumberType()]),
        ("print", ["s"], [StringType()] [VoidType()])
        ("range", ["start", "end"], [NumberType(), NumberType()], [IterableType()]),
    ]
    
def get_builtin_constants() -> dict[str, Type]:
    return {
        "PI":NumberType(),
        "E":NumberType()
    }