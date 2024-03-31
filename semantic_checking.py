from utils.semantic import Context, SemanticError, Type
import utils.visitor as visitor
from hulk_ast import *
from errors import *
import hulk_builtins

class TypeCollector:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.context: Context = Context()
        
    @visitor.on("node")
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):       
        for builtin in hulk_builtins.get_builtin_types():
            self.context.add_type(builtin)
        
        for builtin in hulk_builtins.get_builtin_functions():
            self.context.add_global_function(*builtin)
        
        for dec in node.declarations:
            self.visit(dec)
            
    @visitor.when(TypeDeclarationNode)
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
        
    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for dec in node.declarations:
            self.visit(dec)
            
    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode):
        self.current_type = self.context.get_type(node.id)
        
        if node.parent is not None:
            parent_type = self.context.get_type(node.parent)
            if not parent_type.can_be_inherited_from:
                self.errors.append(INVALID_INHERITANCE % node.parent)
            else:
                try:
                    self.current_type.set_parent(parent_type)
                except SemanticError as e:
                    self.errors.append(e.text)
        
        for f in node.features:
            self.visit(f)
        
    @visitor.when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode):
        pass