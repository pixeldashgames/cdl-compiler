from utils.ast import Node, AtomicNode, BinaryNode, UnaryNode
from errors import *
from hulk_interpreter import InterpreterContext, InterpreterScope, Value, Variable
import hulk_builtins
from utils.semantic import AnyType, BooleanType, Context, NumberType, SemanticError, StringType, Type

class ProgramNode(Node):
    def __init__(self, declarations):
        self.declarations = declarations
        
    def evaluate(self, semantic_context: Context, interpreter_context: InterpreterContext, scope: InterpreterScope = None):
        scope = InterpreterScope()
        
        for node in self.declarations:
            if getattr(node, "__iter__", None) is None:
                continue
            
            for expr in node:
                expr.evaluate(semantic_context, interpreter_context, scope)
        
class DeclarationNode(Node):
    pass

class ExpressionNode(Node):
    pass

class TypeDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, features, p_params, parent=None):
        self.id = idx
        self.params: list[ParamNode] = params
        self.parent = parent
        self.p_params = p_params
        self.features = features
    
    def evaluate(self, param_values: list[Value], semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        value = {}
        
        parent_params = param_values
        
        if self.params:
            for param, value in zip(self.params, param_values):
                if param.type is None:
                    param_type = value.value_type
                else:
                    param_type = semantic_context.get_type(param.type)
                scope.define_variable(param.id, param_type, value.value, value.value_type)

            if self.parent is not None:
                parent_params = [p.evaluate(semantic_context, context, scope.create_child()) for p in self.p_params]
                
        if self.parent is not None:
            parent_type = semantic_context.get_type(self.parent)
            
            value = context.get_type_declaration(parent_type)\
                .evaluate(parent_params, semantic_context, context, scope.create_child()).value

        this_type = semantic_context.get_type(self.id)
        attrs = context.get_attributes(this_type)
        if attrs:
            for a in attrs:
                attr_val = a.evaluate(semantic_context, context, scope.create_child())
                if a.type is None:
                    attr_type = attr_val.value_type
                else:
                    attr_type = semantic_context.get_type(a.type)
                value[a.id] = Variable(a.id, attr_type, attr_val.value, attr_val.value_type)
        
        return Value(value, this_type)

class FuncDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, body, return_type=None):
        self.id = idx
        self.params = params
        self.type = return_type
        self.body = body
        
    def evaluate(self, param_values: list[Value], semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        for param, value in zip(self.params, param_values):
            if param.type is not None:
                param_type = semantic_context.get_type(param.type)
            else:
                param_type = value.value_type
            scope.define_variable(param.id, param_type, value.value, value.value_type)
        
        fun_scope = scope.create_child()
        
        for i, expr in enumerate(self.body):
            value = expr.evaluate(semantic_context, context, fun_scope)
            if i == len(self.body) - 1:
                return value
                    
class MethDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, body, return_type=None):
        self.id = idx
        self.params = params
        self.type = return_type
        self.body = body
        
    def evaluate(self, param_values: list[object], semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        for param, value in zip(self.params, param_values):
            if param.type is not None:
                param_type = semantic_context.get_type(param.type)
            else:
                param_type = value.value_type
            scope.define_variable(param.id, param_type, value.value, value.value_type)
        
        fun_scope = scope.create_child()
        
        for i, expr in enumerate(self.body):
            value = expr.evaluate(semantic_context, context, fun_scope)
            if i == len(self.body) - 1:
                return value

class AttrDeclarationNode(DeclarationNode):
    def __init__(self, idx, expr, typex=None):
        self.id = idx
        self.expr = expr
        self.type = typex
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        return self.expr.evaluate(semantic_context, context, scope)

class ParamNode(DeclarationNode):
    def __init__(self, idx, typex=None):
        self.id = idx
        self.type = typex
        
    def evaluate(self):
        raise RuntimeError(CANT_EVALUATE_ERROR % "ParamNode")

class VarDeclarationNode(ExpressionNode):
    def __init__(self, asignations, expr, typex=None):
        self.asignations = asignations
        self.type = typex
        self.expr = expr
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        current_scope = scope
        for a in self.asignations:
            current_scope = current_scope.create_child()
            expr_value = a.evaluate(semantic_context, context, current_scope)
            if a.type is not None:
                var_type = semantic_context.get_type(a.type)
            else:
                var_type = expr_value.value_type
            current_scope.define_variable(a.id, var_type, expr_value.value, expr_value.value_type)
        
        return self.expr.evaluate(semantic_context, context, current_scope)

class AssignNode(ExpressionNode):
    def __init__(self, idx, expr, typex=None):
        self.id = idx
        self.type = typex
        self.expr = expr
        
    def evaluate(self):
        raise RuntimeError(CANT_EVALUATE_ERROR % "ParamNode")

class DesAssignNode(ExpressionNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        expr_value = self.expr.evaluate(semantic_context, context, scope)
        scope.modify_variable(self.id, expr_value.value, expr_value.value_type)
        return expr_value

class MethCallNode(ExpressionNode):
    def __init__(self, obj, idx, args):
        self.obj = obj
        self.id = idx
        self.args = args
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        self_var = self.obj.evaluate(semantic_context, context, scope.create_child())
        if isinstance(self.obj, VariableNode):
            var = scope.find_variable(self.obj.lex)
            if var:
                var_type = var.type
            elif self.obj.lex == "self":
                var_type = scope.self_var[0]
            else:
                var_type = self_var.value_type
        else: 
            var_type = self_var.value_type
        
        param_values = [a.evaluate(semantic_context, context, scope.create_child()) for a in self.args]
        
        func_scope = InterpreterScope()
        func_scope.define_self_var(var_type, self_var, self.id)
        
        return context.get_method(var_type, self.id).evaluate(param_values, semantic_context, context, func_scope)
        

class FunCallNode(ExpressionNode):
    def __init__(self, idx, args):
        self.id = idx
        self.args = args
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        param_values = [a.evaluate(semantic_context, context, scope.create_child()) for a in self.args]
        
        func_scope = InterpreterScope()
        
        func = context.get_global_function(self.id)
        
        if not func:
            if self.id == "base":
                return context.get_method(scope.self_var[0].parent, scope.self_var[2])\
                    .evaluate(param_values, semantic_context, context, scope)
            
            builtin_functions = hulk_builtins.get_builtin_functions()
            builtin_functions = [f for f in builtin_functions if f[0] == self.id]
            if builtin_functions:
                return Value(hulk_builtins.execute_builtin_function(builtin_functions[0][0], 
                                                                    param_values, 
                                                                    semantic_context, 
                                                                    context, func_scope), builtin_functions[0][3])
            raise RuntimeError(FUNCTION_NOT_FOUND % self.id)
        return func.evaluate(param_values, semantic_context, context, func_scope)

class ConditionalNode(ExpressionNode):
    def __init__(self, conds):
        self.conds = conds
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        for c in self.conds:
            if isinstance(c, ElseNode):
                return c.evaluate(semantic_context, context, scope.create_child())
            if c.cond.evaluate(semantic_context, context, scope.create_child()).value == True:
                return c.evaluate(semantic_context, context, scope.create_child())
        return None

        
class IfNode(ExpressionNode):
    def __init__(self, cond, expr):
        self.cond = cond
        self.expr = expr
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        for i, expr in enumerate(self.expr):
            value = expr.evaluate(semantic_context, context, scope)
            if i == len(self.expr) - 1:
                return value

class ElseNode(ExpressionNode):
    def __init__(self, expr):
        self.expr = expr
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        for i, expr in enumerate(self.expr):
            value = expr.evaluate(semantic_context, context, scope)
            if i == len(self.expr) - 1:
                return value

class ElifNode(ExpressionNode):
    def __init__(self, cond, expr):
        self.cond = cond
        self.expr = expr
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        for i, expr in enumerate(self.expr):
            value = expr.evaluate(semantic_context, context, scope)
            if i == len(self.expr) - 1:
                return value

class WhileNode(ExpressionNode):
    def __init__(self, cond, expr):
        self.cond = cond
        self.expr = expr
    
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        cond_scope = scope.create_child()
        expr_scope = scope.create_child()
        
        last_result = None
        while self.cond.evaluate(semantic_context, context, cond_scope).value == True:
            for expr in self.expr:
                last_result = expr.evaluate(semantic_context, context, expr_scope)
        return last_result
        
class ForNode(ExpressionNode):
    def __init__(self, var, iter, expr):
        self.var = var
        self.iter = iter
        self.expr = expr
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        raise RuntimeError("Error 418 I'm a teapot. I can't brew coffee")

class AsNode(ExpressionNode):
    def __init__(self, expr, typex):
        self.expr = expr
        self.type = typex
    
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        expr_value = self.expr.evaluate(semantic_context, context, scope.create_child())
        
        as_type = semantic_context.get_type(self.type)
        
        if not expr_value.value_type.conforms_to(as_type):
            raise RuntimeError(ERROR_DOWNCASTING % as_type.name)
        
        return Value(expr_value.value, as_type)

class InstantiateNode(ExpressionNode):
    def __init__(self, idx, args):
        self.id = idx
        self.args = args
        
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        param_values = [a.evaluate(semantic_context, context, scope.create_child()) for a in self.args]
        
        instance_type = semantic_context.get_type(self.id)
        
        return context.get_type_declaration(instance_type).evaluate(param_values, semantic_context, context, InterpreterScope())


class ConstantNumNode(AtomicNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        return Value(float(self.lex), NumberType())

class StringNode(AtomicNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        return Value(self.lex[1:-1], StringType())

class BoolNode(AtomicNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        return Value(self.lex == "true", BooleanType())

class VariableNode(AtomicNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        var = scope.find_variable(self.lex)
        
        if not var:
            if self.lex == "self":
                return Value(scope.self_var[1].value, scope.self_var[0])
            constants = hulk_builtins.get_builtin_constants()
            if self.lex in constants:
                return Value(hulk_builtins.get_constant_value(self.lex), constants[self.lex])
            raise RuntimeError(VARIABLE_NOT_FOUND % self.lex)
        
        return Value(var.value, var.underlaying_type)


class AttributeNode(AtomicNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        attr_var: Variable = scope.self_var[1].value[self.lex]
        return Value(attr_var.value, attr_var.underlaying_type)

class ArithmeticOperationNode(BinaryNode):
    pass

class PlusNode(ArithmeticOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value + right_val.value, NumberType())

class MinusNode(ArithmeticOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value - right_val.value, NumberType())

class StarNode(ArithmeticOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value * right_val.value, NumberType())

class PowerNode(ArithmeticOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value ** right_val.value, NumberType())

class DivNode(ArithmeticOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value / right_val.value, NumberType())

class CongruenceNode(ArithmeticOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value % right_val.value, NumberType())

class StringOperationNode(BinaryNode):
    pass

class ConcatenateNode(StringOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(str(left_val.value) + str(right_val.value), StringType())

class DoubleConcatenateNode(StringOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(str(left_val.value) + " " + str(right_val.value), StringType())

class BooleanOperationNode(BinaryNode):
    pass

class OrNode(BooleanOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value == True or right_val.value == True, BooleanType())

class AndNode(BooleanOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value == True and right_val.value == True, BooleanType())

class NotNode(UnaryNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        val = self.node.evaluate(semantic_context, context, scope)
        
        return Value(not (val.value == True), BooleanType())

class ComparisonOperationNode(BinaryNode):
    pass

class MinorNode(ComparisonOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value < right_val.value, BooleanType())

class MayorNode(ComparisonOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value > right_val.value, BooleanType())

class EqMinorNode(ComparisonOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value <= right_val.value, BooleanType())

class EqMayorNode(ComparisonOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value >= right_val.value, BooleanType())

class EqualNode(ComparisonOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value == right_val.value, BooleanType())

class DifferentNode(ComparisonOperationNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        right_val = self.right.evaluate(semantic_context, context, scope)
        
        return Value(left_val.value != right_val.value, BooleanType())

class IsNode(BinaryNode):
    def evaluate(self, semantic_context: Context, context: InterpreterContext, scope: InterpreterScope):
        left_val = self.left.evaluate(semantic_context, context, scope)
        
        is_type = semantic_context.get_type(self.right)
        
        return Value(left_val.value_type.conforms_to(is_type), BooleanType())