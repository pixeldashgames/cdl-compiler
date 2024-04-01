# Compile-time errors

INVALID_INHERITANCE = "Inheritance from '%s' is not allowed."
INVALID_TYPE_CONVERSION = "Can't convert from %s to %s."
WRONG_SIGNATURE = "Wrong signature when attempting to override '%s' in %s."
SELF_IS_READONLY = "Can't write to special variable 'self'."
VARIABLE_NOT_DEFINED = "'%s' is not defined in this context."
INCORRECT_NUMBER_OF_ARGS = "Tried to call '%s' with incorrect number of arguments."
INCORRECT_NUMBER_OF_ARGS_IN_PARENT = "Tried to initialize parent '%s' from '%s' with incorrect number of arguments."
INCORRECT_INSTANTIATION = "Can't instantiate type '%s' with those arguments."
INVALID_AS_EXPRESSION = "Can't use 'as' expression between types '%s' and '%s'"
INVALID_ARITHMETIC_OPERATION = "Can't evaluate an arithmetic operation between types '%s' and '%s'"
INVALID_COMPARISON_OPERATION = "Can't evaluate a comparison operation between types '%s' and '%s'"
INVALID_STRING_OPERATION = "Can't evaluate a string operation between types '%s' and '%s'"
INVALID_BOOLEAN_OPERATION = "Can't evaluate a boolean operation between types '%s' and '%s'"
INVALID_NOT = "Can't evaluate 'not' operation on type '%s'"
INVALID_ATTRIBUTE_INVOCATION = "An attribute reference must always be done using the self keyword"

# Runtime error

CANT_EVALUATE_ERROR = "Can't evaluate %s."
VARIABLE_NOT_FOUND = "Couldn't find variable '%s' in this context."
FUNCTION_NOT_FOUND = "Couldn't find function '%s'."
ERROR_DOWNCASTING = "Error downcasting expression to type '%s'"