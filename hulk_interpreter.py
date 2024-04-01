from utils.semantic import Context, Type
import utils.visitor as visitor
from hulk_ast import *
import itertools as itt

class RuntimeError(Exception):
    @property
    def text(self):
        return self.args[0]

class InterpreterContext:
    def __init__(self) -> None:
        self.global_functions: dict[str, FuncDeclarationNode] = {}
        self.methods: dict[Type, dict[str, MethDeclarationNode]] = {}
        self.type_declarations: dict[Type, TypeDeclarationNode] = {}
        self.attribute_declarations: dict[Type, list[AttrDeclarationNode]]
        
    def add_attribute(self, type: Type, node: AttrDeclarationNode):
        if not self.attribute_declarations[type]:
            self.attribute_declarations[type] = [ node ]
        else:
            self.attribute_declarations[type].append(node)    
    
    def add_global_function(self, name: str, node: FuncDeclarationNode):
        self.global_functions[name] = node
        
    def add_type_declaration(self, type: Type, node: TypeDeclarationNode):
        self.type_declarations[type] = node
        
    def add_method(self, name: str, typex: Type, node: MethDeclarationNode):
        if typex not in self.methods:
            self.methods[typex] = { name:node }
        else:
            self.methods[typex][name] = node
            
    def get_global_function(self, name: str):
        return self.global_functions[name]
    
    def get_type_declaration(self, type: Type):
        return self.type_declarations[type]
    
    def get_method(self, type: Type, name: str):
        return self.methods[type][name]
    
    def get_attributes(self, type: Type):
        return self.attribute_declarations[type]
        
            
class InterpreterScope:
    def __init__(self, parent=None):
        self.locals: list[tuple[str, Type, object]] = []
        self.parent = parent
        self.children = []
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.locals)

    def create_child(self):
        child = InterpreterScope(self)
        self.children.append(child)
        return child

    def define_variable(self, vname, vtype, value):
        self.locals.append((vname, vtype, value))
        return (vname, vtype, value)

    def find_variable(self, vname, index=None):
        locals = self.locals if index is None else itt.islice(self.locals, index)
        locals = [x for x in locals if x[0] == vname]
        if not locals:
            return self.parent.find_variable(vname, self.index) if self.parent is not None else None
        return locals[-1]
            
    def is_defined(self, vname):
        return self.find_variable(vname) is not None

    def is_local(self, vname):
        return any(True for x in self.locals if x[0] == vname)
        
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
    
    @visitor.when(MethDeclarationNode)
    def visit(self, node: MethDeclarationNode):
        self.interpreter_context.add_method(node.id, self.current_type, node)
        
    @visitor.when(AttrDeclarationNode)
    def visit(self, node: AttrDeclarationNode):
        self.interpreter_context.add_attribute(self.current_type, node)
        