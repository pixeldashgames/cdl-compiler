from utils.semantic import Context, Type
import utils.visitor as visitor
from errors import *
from hulk_ast import InterpreterContext, ProgramNode, FuncDeclarationNode, TypeDeclarationNode, MethDeclarationNode, AttrDeclarationNode
import itertools as itt

class RuntimeError(Exception):
    @property
    def text(self):
        return self.args[0]
        
class InterpreterCollector:
    def __init__(self, semantic_context: Context) -> None:
        self.semantic_context = semantic_context
        self.interpreter_context = InterpreterContext()
        self.current_type: Type = None
    
    @visitor.on("node")
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for dec in node.declarations:
            self.visit(dec)
            
    @visitor.when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode):
        self.context.add_global_function(node.id, node)
        
    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode):
        self.current_type = self.semantic_context.get_type(node.id)
        
        self.interpreter_context.add_type_declaration(self.current_type, node)
        
        for f in node.features:
            self.visit(f)
        
        if not self.interpreter_context.methods[self.current_type]:
            return
        
        for name, method in self.interpreter_context.methods[self.current_type].items():
            children = [t for t in self.semantic_context.types.values() if t.conforms_to(self.current_type)]
            for c in children:
                if not self.interpreter_context.methods[c] \
                    or not self.interpreter_context.methods[c].get(name, None):
                    self.interpreter_context.add_method(name, c, method)
    
    @visitor.when(MethDeclarationNode)
    def visit(self, node: MethDeclarationNode):
        self.interpreter_context.add_method(node.id, self.current_type, node)
        
    @visitor.when(AttrDeclarationNode)
    def visit(self, node: AttrDeclarationNode):
        self.interpreter_context.add_attribute(self.current_type, node)
        