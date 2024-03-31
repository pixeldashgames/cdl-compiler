from utils.semantic import Context, SemanticError, Type, ErrorType, VoidType, AnyType
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
        
        for arg in node.params:
            if arg.type is None:
                arg_type = AnyType()
            else:
                try:
                    arg_type = self.context.get_type(arg.type)
                except SemanticError as e:
                    arg_type = ErrorType()
                    self.errors.append(e.text)
            node.params.append((arg.id, arg_type))
        
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
        
        self.current_type = None
        
    @visitor.when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode):
        param_names = []
        param_types = []
        
        for p in node.params:
            p: ParamNode = p
            param_names.append(p.id)
            if p.type is None:
                param_types.append(AnyType())
            else:
                try:
                    param_types.append(self.context.get_type(p.type))
                except SemanticError as e:
                    self.errors.append(e.text)
                    param_types.append(ErrorType())
        
        if node.type == None:
            return_type = AnyType()
        if node.type == "void":
            return_type = VoidType()
        else:        
            try:
                return_type = self.context.get_type(node.type)
            except SemanticError as e:
                self.errors.append(e.text)
                return_type = ErrorType()
            
        if self.current_type is not None:
            try:
                self.current_type.define_method(node.id, param_names, param_types, return_type)
            except SemanticError as e:
                self.errors.append(e.text)
        else:
            try:
                self.context.add_global_function(node.id, param_names, param_types, return_type)
            except SemanticError as e:
                self.errors.append(e.text)
            
    @visitor.when(AttrDeclarationNode)
    def visit(self, node: AttrDeclarationNode):
        if node.type is None:
            attr_type = AnyType()
        else:
            try:
                attr_type = self.context.get_type(node.type)
            except SemanticError as e:
                self.errors.append(e.text)
                attr_type = ErrorType()
        
        try:
            self.current_type.define_attribute(node.id, attr_type)
        except SemanticError as e:
            self.errors.append(e.text)


class TypeChecker:
    pass