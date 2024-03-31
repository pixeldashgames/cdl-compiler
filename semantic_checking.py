from utils.semantic import Context, SemanticError, Type
import utils.visitor as visitor
from hulk_ast import *
import hulk_builtins

class TypeCollector:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.context: Context = Context()
        
    @visitor.on("node")
    def visit(self, node):
        pass
    
    @visitor.on(ProgramNode)
    def visit(self, node: ProgramNode):       
        for builtin in hulk_builtins.get_builtin_types():
            self.context.add_type(builtin)
        
        for builtin in hulk_builtins.get_builtin_functions():
            self.context.add_global_function(*builtin)
        
        for dec in node.declarations:
            self.visit(dec)
            
    @visitor.on(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode):
        try:
            self.context.create_type(node.id)
        except SemanticError as e:
            self.errors.append(e.text)
            
class TypeBuilder:
    def __init__(self, context: Context, errors: list[str]) -> None:
        self.context: Context = context
        self.errors: list[str] = errors
        self.current_type: Type = None
        
    @visitor.on("node")
    def visit(self, node):
        pass
        
    @visitor.on(ProgramNode)
    def visit(self, node: ProgramNode):
        for dec in node.declarations:
            self.visit(dec)