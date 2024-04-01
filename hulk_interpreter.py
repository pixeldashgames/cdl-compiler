from utils.semantic import Context, Type
import utils.visitor as visitor
from hulk_ast import *
import itertools as itt

class RuntimeError(Exception):
    @property
    def text(self):
        return self.args[0]

class Variable:
    def __init__(self, id, type, value, underlaying_type) -> None:
        self.id: str = id
        self.type: Type = type
        self.value: object = value
        self.underlaying_type: Type = underlaying_type

class Value:
    def __init__(self, value, value_type) -> None:
        self.value: object = value
        self.value_type: Type = value_type

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
        return self.global_functions.get(name, None)
    
    def get_type_declaration(self, type: Type):
        return self.type_declarations.get(type, None)
    
    def get_method(self, type: Type, name: str):
        type_methods = self.methods.get(type, None)
        if not type_methods:
            return None
        return type_methods.get(name, None)
    
    def get_attributes(self, type: Type):
        return self.attribute_declarations.get(type, None)
        
            
class InterpreterScope:
    def __init__(self, parent=None):
        self.locals: list[Variable] = []
        self.self_var: tuple[Type, Value, str] = None
        self.parent = parent
        self.children = []
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.locals)

    def create_child(self):
        child = InterpreterScope(self)
        self.children.append(child)
        return child

    def define_self_var(self, type: Type, value: Value, method_id: str):
        self.self_var = (type, value, method_id)

    def define_variable(self, vname, vtype, value, value_type):
        var = Variable(vname, vtype, value, value_type)
        self.locals.append(var)
        return var

    def modify_variable(self, vname, value, value_type, index=None):
        locals = self.locals if index is None else itt.islice(self.locals, index)
        vars = [(i, x) for i, x in enumerate(locals) if x.id == vname]
        if not vars:
            if self.parent is not None:
                self.parent.modify_variable(vname, value, value_type, self.index)
                return
            raise RuntimeError(VARIABLE_NOT_FOUND % vname)
        (i, var) = vars[-1]
        self.locals[i] = Variable(var.id, var.type, value, value_type)
        
    def find_variable(self, vname, index=None):
        locals = self.locals if index is None else itt.islice(self.locals, index)
        locals = [x for x in locals if x.id == vname]
        if not locals:
            return self.parent.find_variable(vname, self.index) if self.parent is not None else None
        return locals[-1]
            
    def is_defined(self, vname):
        return self.find_variable(vname) is not None

    def is_local(self, vname):
        return any(True for x in self.locals if x.id == vname)
        
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
        