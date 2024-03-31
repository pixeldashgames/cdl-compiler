from utils.ast import Node, AtomicNode, BinaryNode, UnaryNode

class ProgramNode(Node):
    def __init__(self, declarations):
        self.declarations = declarations

class DeclarationNode(Node):
    pass

class ExpressionNode(Node):
    pass

class TypeDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, features, p_params, parent=None):
        self.id = idx
        self.params = params
        self.parent = parent
        self.p_params = p_params
        self.features = features

class FuncDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, body, return_type=None):
        self.id = idx
        self.params = params
        self.type = return_type
        self.body = body

class MethDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, body, return_type=None):
        self.id = idx
        self.params = params
        self.type = return_type
        self.body = body

class AttrDeclarationNode(DeclarationNode):
    def __init__(self, idx, expr, typex=None):
        self.id = idx
        self.expr = expr
        self.type = typex

class ParamNode(DeclarationNode):
    def __init__(self, idx, typex=None):
        self.id = idx
        self.type = typex

class VarDeclarationNode(ExpressionNode):
    def __init__(self, asignations, expr, typex=None):
        self.asignations = asignations
        self.type = typex
        self.expr = expr

class AssignNode(ExpressionNode):
    def __init__(self, idx, expr, typex=None):
        self.id = idx
        self.type = typex
        self.expr = expr

class DesAssignNode(ExpressionNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr

class MethCallNode(ExpressionNode):
    def __init__(self, obj, idx, args):
        self.obj = obj
        self.id = idx
        self.args = args

class FunCallNode(ExpressionNode):
    def __init__(self, idx, args):
        self.id = idx
        self.args = args

class ConditionalNode(ExpressionNode):
    def __init__(self, conds):
        self.conds = conds
        
class IfNode(ExpressionNode):
    def __init__(self, cond, expr):
        self.cond = cond
        self.expr = expr

class ElseNode(ExpressionNode):
    def __init__(self, expr):
        self.expr = expr

class ElifNode(ExpressionNode):
    def __init__(self, cond, expr):
        self.cond = cond
        self.expr = expr

class WhileNode(ExpressionNode):
    def __init__(self, cond, expr):
        self.cond = cond
        self.expr = expr

class ForNode(ExpressionNode):
    def __init__(self, var, iter, expr):
        self.var = var
        self.iter = iter
        self.expr = expr

class AsNode(ExpressionNode):
    def __init__(self, expr, typex):
        self.expr = expr
        self.type = typex

class InstantiateNode(ExpressionNode):
    def __init__(self, idx, args):
        self.id = idx
        self.args = args

class ConstantNumNode(AtomicNode):
    pass

class StringNode(AtomicNode):
    pass

class BoolNode(AtomicNode):
    pass

class VariableNode(AtomicNode):
    pass

class ArithmeticOperationNode(BinaryNode):
    pass

class PlusNode(ArithmeticOperationNode):
    pass

class MinusNode(ArithmeticOperationNode):
    pass

class StarNode(ArithmeticOperationNode):
    pass

class DivNode(ArithmeticOperationNode):
    pass

class CongruenceNode(ArithmeticOperationNode):
    pass

class StringOperationNode(BinaryNode):
    pass

class ConcatenateNode(StringOperationNode):
    pass

class DoubleConcatenateNode(StringOperationNode):
    pass

class BooleanOperationNode(BinaryNode):
    pass

class OrNode(BooleanOperationNode):
    pass

class AndNode(BooleanOperationNode):
    pass

class NotNode(UnaryNode):
    pass

class ComparisonOperationNode(BinaryNode):
    pass

class MinorNode(ComparisonOperationNode):
    pass

class MayorNode(ComparisonOperationNode):
    pass

class EqMinorNode(ComparisonOperationNode):
    pass

class EqMayorNode(ComparisonOperationNode):
    pass

class EqualNode(ComparisonOperationNode):
    pass

class DifferentNode(ComparisonOperationNode):
    pass

class IsNode(BinaryNode):
    pass