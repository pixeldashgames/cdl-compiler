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

class PlusNode(BinaryNode):
    pass

class MinusNode(BinaryNode):
    pass

class StarNode(BinaryNode):
    pass

class DivNode(BinaryNode):
    pass

class CongruenceNode(BinaryNode):
    pass

class ConcatenateNode(BinaryNode):
    pass

class DoubleConcatenateNode(BinaryNode):
    pass

class OrNode(BinaryNode):
    pass

class AndNode(BinaryNode):
    pass

class NotNode(UnaryNode):
    pass

class MinorNode(BinaryNode):
    pass

class MayorNode(BinaryNode):
    pass

class EqMinorNode(BinaryNode):
    pass

class EqMayorNode(BinaryNode):
    pass

class EqualNode(BinaryNode):
    pass

class DifferentNode(BinaryNode):
    pass

class IsNode(BinaryNode):
    pass