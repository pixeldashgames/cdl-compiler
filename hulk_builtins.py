from utils.semantic import *
from math import sqrt, sin, cos, exp, log, pi, e
from random import random

def get_builtin_types() -> list[Type]:
    return [ObjectType(), StringType(), NumberType(), BooleanType(), IterableType()]

def get_builtin_functions() -> list[tuple[str, list[str], list[Type], Type]]:
    return [
        ("sqrt", ["x"], [NumberType()], NumberType()),
        ("sin", ["x"], [NumberType()], NumberType()),
        ("cos", ["x"], [NumberType()], NumberType()),
        ("exp", ["x"], [NumberType()], NumberType()),
        ("log", ["b", "x"], [NumberType(), NumberType()], NumberType()),
        ("rand", [], [], NumberType()),
        ("print", ["s"], [StringType()], VoidType())
    ]
    
def get_builtin_constants() -> dict[str, Type]:
    return {
        "PI":NumberType(),
        "E":NumberType()
    }
    
constants = {
    "PI": pi,
    "E": e
}
    
def get_constant_value(const: str):
    return constants[const]

builtin_functions = {
    "sqrt": lambda x: sqrt(x),
    "sin": lambda x: sin(x),
    "cos": lambda x: cos(x), 
    "exp": lambda x: exp(x), 
    "log": lambda b, x: log(x, b),
    "rand": lambda: random(),
    "print": lambda s: print(s)
}

def execute_builtin_function(func: str, param_values, semantic_context,
                             context, scope):
    try:
        if len(param_values) == 0:
            return builtin_functions[func]()
        if len(param_values) == 1:
            return builtin_functions[func](param_values[0].value)
        if len(param_values) == 2:
            return builtin_functions[func](param_values[0].value, param_values[1].value)
    except:
        raise RuntimeError("Invalid parameters for built-in function '%s'." % func)
    raise RuntimeError("Invalid parameters for built-in function '%s'." % func)