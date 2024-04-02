from utils.semantic import BooleanType, Context, IterableType, Method, Attribute, NumberType, Scope, SemanticError, StringType, Type, ErrorType, VariableInfo, VoidType, AnyType
import utils.visitor as visitor
from hulk_ast import *
from errors import *
import hulk_builtins


def run_semantic_checker(ast) -> bool:
    errors = []
    found_errors = False
    
    print('============== COLLECTING TYPES ===============')
    collector = TypeCollector(errors)
    collector.visit(ast)
    context = collector.context
    print('Type collection errors:\n', "\n".join(errors))
    print('Context:')
    print(context)
    
    if errors:
        found_errors = True
    
    print('=============== BUILDING TYPES ================')
    builder = TypeBuilder(context, errors)
    builder.visit(ast)
    print('Type building errors:\n', "\n".join(errors))
    print('Context:')
    print(context)
    
    if errors:
        found_errors = True
        
    print('=============== CHECKING TYPES ================')
    checker = TypeChecker(context, errors)
    checker.visit(ast)
    print('Type checking errors:\n', "\n".join(errors))
    print('Context:')
    print(context)
    
    if errors:
        found_errors = True
        
    return context if not found_errors else None


class TypeCollector:
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
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
            self.current_type.args.append((arg.id, arg_type))
        
        if node.parent is not None:
            parent_type = self.context.get_type(node.parent)
            
            if node.p_params:
                self.current_type.constructed_parent = True
            
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
        
    @visitor.when(MethDeclarationNode)
    def visit(self, node: MethDeclarationNode):
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
        elif node.type == "void":
            return_type = VoidType()
        else:        
            try:
                return_type = self.context.get_type(node.type)
            except SemanticError as e:
                self.errors.append(e.text)
                return_type = ErrorType()
            
        try:
            self.current_type.define_method(node.id, param_names, param_types, return_type)
        except SemanticError as e:
            self.errors.append(e.text)
 
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
        
        if node.type is None:
            return_type = AnyType()
        elif node.type == "void":
            return_type = VoidType()
        else:
            try:
                return_type = self.context.get_type(node.type)
            except SemanticError as e:
                self.errors.append(e.text)
                return_type = ErrorType()
            
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
    def __init__(self, context: Context, errors: list[str]) -> None:
        self.context = context
        self.errors = errors
        self.current_type: Type = None
        self.current_method: Method = None
    
    @visitor.on("node")
    def visit(self, node, scope):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, scope: Scope = None):
        scope = Scope()
        for d in node.declarations:
            if getattr(d, "__iter__", None) is not None:
                entry_scope = scope.create_child()
                for st in d:
                    self.visit(st, entry_scope)
            else:
                self.visit(d, scope.create_child())
            
    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode, scope: Scope = None):
        this_type = self.context.get_type(node.id)
        self.current_type = this_type
        
        parent_construction_scope = scope.create_child()
        for var, type in self.current_type.get_args():
            parent_construction_scope.define_variable(var, type)
        
        if this_type.parent and node.p_params:
            parent_args = this_type.parent.get_args()
            
            if len(parent_args) != len(node.p_params):
                self.errors.append(INCORRECT_NUMBER_OF_ARGS_IN_PARENT % (this_type.parent.name, this_type.name))
            else:
                for i, param in enumerate(node.p_params):
                    param_type = self.visit(param, parent_construction_scope)
                    if not param_type.conforms_to(parent_args[i][1]):
                        self.errors.append(INVALID_TYPE_CONVERSION % (param_type.name, parent_args[i][1].name))
        
        class_scope: Scope = scope.create_child()
        
        for f in node.features:
            self.visit(f, class_scope)
        
        self.current_type = None
        
        return this_type
    
    @visitor.when(AttrDeclarationNode)
    def visit(self, node: AttrDeclarationNode, scope: Scope = None):
        initialization_scope = scope.create_child()
        attr: Attribute = self.current_type.get_attribute(node.id)
        
        for var, type in self.current_type.get_args():
            initialization_scope.define_variable(var, type)
        
        expr_type: Type = self.visit(node.expr, initialization_scope)
        
        if attr.type == AnyType():
            attr.type = expr_type
        
        if not expr_type.conforms_to(attr.type):
            self.errors.append(INVALID_TYPE_CONVERSION % (expr_type.name, attr.type.name))
        
        return attr.type
    
    @visitor.when(MethDeclarationNode)
    def visit(self, node: MethDeclarationNode, scope: Scope = None):
        self.current_method = self.current_type.get_method(node.id)
        
        fun_scope = scope.create_child()
        
        for param, type in zip(self.current_method.param_names, self.current_method.param_types):
            fun_scope.define_variable(param, type)
        
        s_type = None
        for i, statement in enumerate(node.body):
            s_type = self.visit(statement, fun_scope)
            if i == len(node.body) - 1 and self.current_method != VoidType() \
                and not s_type.conforms_to(self.current_method.return_type):
                self.errors.append(INVALID_TYPE_CONVERSION % (s_type.name, node.type))
        
        if self.current_method.return_type == AnyType() and s_type is not None:
            self.current_method.return_type = s_type
        
        if self.current_type.parent is not None:
            try:
                conforming_method = self.current_type.parent.get_method(node.id)
                if len(conforming_method.param_types) != len(self.current_method.param_types) \
                    or not all([t_a == t_b for t_a, t_b in 
                            zip(conforming_method.param_types, 
                                self.current_method.param_types)]) or \
                conforming_method.return_type != self.current_method.return_type:
                    self.errors.append(WRONG_SIGNATURE % (node.id, self.current_type.name))
            except SemanticError:
                pass
        
        ret_type = self.current_method.return_type
        
        self.current_method = None
        
        return ret_type
    
    @visitor.when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, scope: Scope = None):
        self.current_method = self.context.get_global_function(node.id)
        
        fun_scope = scope.create_child()
        
        for param, type in zip(self.current_method.param_names, self.current_method.param_types):
            fun_scope.define_variable(param, type)
        
        for i, statement in enumerate(node.body):
            s_type = self.visit(statement, fun_scope)
            if i == len(node.body) - 1 and self.current_method.return_type != VoidType() \
                and not s_type.conforms_to(self.current_method.return_type):
                self.errors.append(INVALID_TYPE_CONVERSION % (s_type.name, node.type.name))
        
        ret_type = self.current_method.return_type
        
        self.current_method = None
        
        return ret_type
    
    @visitor.when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode, scope: Scope = None):       
        current_scope = scope
        for assig in node.asignations:
            current_scope = current_scope.create_child()
            self.visit(assig, current_scope)
        
        for i, expr in enumerate(node.expr):
            expr_type = self.visit(expr, current_scope)
            if i == len(node.expr) - 1:
                return expr_type
    
    @visitor.when(AssignNode)
    def visit(self, node: AssignNode, scope: Scope = None):
        expr_type: Type = self.visit(node.expr, scope.create_child())
        
        if node.type is None:
            var_type = expr_type
        else:
            try:
                var_type = self.context.get_type(node.type)
            except SemanticError as e:
                self.errors.append(e.text)
                var_type = ErrorType()
       
        if expr_type == VoidType():
            self.errors.append(CANT_ASSIGN_TO_VOID)
            return ErrorType()
       
        if not expr_type.conforms_to(var_type):
            self.errors.append(INVALID_TYPE_CONVERSION % (expr_type.name, var_type.name))

        scope.define_variable(node.id, var_type)
            
        return var_type
    
    @visitor.when(DesAssignNode)
    def visit(self, node: DesAssignNode, scope: Scope = None):
        if node.attr_id is not None and node.id != "self":
            self.errors.append(INVALID_ATTRIBUTE_INVOCATION)
            return ErrorType()

        if node.attr_id is not None:
            if self.current_type is None:
                self.errors.append(INVALID_ATTRIBUTE_INVOCATION)
                return ErrorType()
            try:
                attr = self.current_type.get_attribute(node.right_id)
                return attr.type
            except SemanticError as e:
                self.errors.append(e.text)
                return ErrorType()

        expr_type = self.visit(node.expr, scope.create_child())
        if node.id == "self" and not scope.is_defined("self"):
            self.errors.append(SELF_IS_READONLY)
            return ErrorType()
        
        if not scope.is_defined(node.id):
            self.errors.append(VARIABLE_NOT_DEFINED % node.id)
            return ErrorType()
        
        var: VariableInfo = scope.find_variable(node.id)
        
        if not expr_type.conforms_to(var.type):
            self.errors.append(INVALID_TYPE_CONVERSION % (expr_type.name, var.type.name))
            
        return var.type
    
    @visitor.when(MethCallNode)
    def visit(self, node: MethCallNode, scope: Scope = None):
        obj_type: Type = self.visit(node.obj, scope.create_child())
        
        try:
            method: Method = obj_type.get_method(node.id)
        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()
        
        if len(node.args) != len(method.param_names):
            self.errors.append(INCORRECT_NUMBER_OF_ARGS % node.id)
            return method.return_type
        
        for i, arg in enumerate(node.args):
            arg_type = self.visit(arg, scope.create_child())
            if not arg_type.conforms_to(method.param_types[i]):
                self.errors.append(INVALID_TYPE_CONVERSION % (arg_type.name, method.param_types[i].name))
        
        return method.return_type
    
    @visitor.when(FunCallNode)
    def visit(self, node: FunCallNode, scope: Scope = None):
        if self.current_method is not None and self.current_type is not None \
            and self.current_type.parent is not None and node.id == "base" and len(node.args) == 0:
                try:
                    self.current_type.parent.get_method(node.id)
                    return self.current_type.parent
                except SemanticError as e:
                    pass
        
        try:
            method: Method = self.context.get_global_function(node.id)
        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()
        
        if len(node.args) != len(method.param_names):
            self.errors.append(INCORRECT_NUMBER_OF_ARGS % node.id)
            return method.return_type
        
        for i, arg in enumerate(node.args):
            arg_type = self.visit(arg, scope.create_child())
            if not arg_type.conforms_to(method.param_types[i]):
                self.errors.append(INVALID_TYPE_CONVERSION % (arg_type.name, method.param_types[i].name))
        
        return method.return_type
    
    @visitor.when(ConditionalNode)
    def visit(self, node: ConditionalNode, scope: Scope = None):
        general_type = None
        for cond in node.conds:
            c_type = self.visit(cond, scope.create_child())
            if general_type is None:
                general_type = c_type
            elif general_type != c_type:
                general_type = AnyType()
        return general_type
    
    @visitor.when(IfNode)
    def visit(self, node: IfNode, scope: Scope = None):
        cond_type = self.visit(node.cond, scope.create_child())
        if cond_type != BooleanType():
            self.errors.append(INVALID_TYPE_CONVERSION % (cond_type.name, BooleanType().name))
            
        expr_scope = scope.create_child()
        for i, expr in enumerate(node.expr):
            expr_type = self.visit(expr, expr_scope)
            if i == len(node.expr) - 1:
                return expr_type
            
    @visitor.when(ElifNode)
    def visit(self, node: ElifNode, scope: Scope = None):
        cond_type = self.visit(node.cond, scope.create_child())
        if cond_type != BooleanType():
            self.errors.append(INVALID_TYPE_CONVERSION % (cond_type.name, BooleanType().name))
            
        expr_scope = scope.create_child()
        for i, expr in enumerate(node.expr):
            expr_type = self.visit(expr, expr_scope)
            if i == len(node.expr) - 1:
                return expr_type
            
    @visitor.when(ElseNode)
    def visit(self, node: ElseNode, scope: Scope = None):
        expr_scope = scope.create_child()
        for i, expr in enumerate(node.expr):
            expr_type = self.visit(expr, expr_scope)
            if i == len(node.expr) - 1:
                return expr_type
    
    @visitor.when(WhileNode)
    def visit(self, node: WhileNode, scope: Scope = None):
        cond_type = self.visit(node.cond, scope.create_child())
        if cond_type != BooleanType():
            self.errors.append(INVALID_TYPE_CONVERSION % (cond_type.name, BooleanType().name))
            
        expr_scope = scope.create_child()
        for i, expr in enumerate(node.expr):
            expr_type = self.visit(expr, expr_scope)
            if i == len(node.expr) - 1:
                return expr_type

    @visitor.when(ForNode)
    def visit(self, node: ForNode, scope: Scope = None):
        iter_type = self.visit(node.iter, scope.create_child())
        
        if not iter_type.conforms_to(IterableType()):
            self.errors.append(INVALID_TYPE_CONVERSION % (iter_type.name, IterableType().name))
        
        expr_scope = scope.create_child()
            
        expr_scope.define_variable(node.var, AnyType())
            
        for i, expr in enumerate(node.expr):
            expr_type = self.visit(expr, expr_scope)
            if i == len(node.expr) - 1:
                return expr_type
            
    @visitor.when(AsNode)
    def visit(self, node: AsNode, scope: Scope = None):
        expr_type = self.visit(node.expr, scope.create_child())
        
        try:
            if not isinstance(node.type, VariableNode):
                self.errors.append(INVALID_AS_EXPRESSION % (expr_type, node.type))
                as_type = ErrorType()
            else:
                as_type = self.context.get_type(node.type.lex)
        except SemanticError as e:
            self.errors.append(e.text)
            as_type = ErrorType()
        
        if not as_type.conforms_to(expr_type):
            self.errors.append(INVALID_AS_EXPRESSION % (expr_type.name, as_type.name))
        
        return as_type
    
    @visitor.when(ConstantNumNode)
    def visit(self, node: ConstantNumNode, scope: Scope = None):
        return NumberType()
    
    @visitor.when(StringNode)
    def visit(self, node: StringNode, scope: Scope = None):
        return StringType()
    
    @visitor.when(BoolNode)
    def visit(self, node: BoolNode, scope: Scope = None):
        return BooleanType()
    
    @visitor.when(VariableNode)
    def visit(self, node: VariableNode, scope: Scope = None):
        if not scope.is_defined(node.lex):
            if self.current_type is not None and self.current_method is not None \
                and node.lex == "self":
                return self.current_type
            
            constants_types = hulk_builtins.get_builtin_constants()
            if node.lex in constants_types:
                return constants_types[node.lex]
                        
            self.errors.append(VARIABLE_NOT_DEFINED % node.lex)
            return ErrorType()
        
        var = scope.find_variable(node.lex)
        return var.type
    
    @visitor.when(AttributeNode)
    def visit(self, node: AttributeNode, scope: Scope = None):
        if not isinstance(node.left_id, VariableNode) or node.left_id.lex != "self":
            self.errors.append(INVALID_ATTRIBUTE_INVOCATION)
            return ErrorType()

        try:
            attr = self.current_type.get_attribute(node.right_id)
        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()
        
        return attr.type
    
    @visitor.when(InstantiateNode)
    def visit(self, node: InstantiateNode, scope: Scope = None):
        try:
            type = self.context.get_type(node.id)
        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()
        
        type_args = type.get_args()
        
        if len(node.args) != len(type_args):
            self.errors.append(INCORRECT_INSTANTIATION % node.id)
        
        for i, arg in enumerate(node.args):
            arg_type = self.visit(arg, scope.create_child())
            if not arg_type.conforms_to(type_args[i][1]):
                self.errors.append(INVALID_TYPE_CONVERSION % (arg_type.name, type_args[i][1].name))
        return type
    
    @visitor.when(ArithmeticOperationNode)
    def visit(self, node: ArithmeticOperationNode, scope: Scope = None):
        left_type = self.visit(node.left, scope.create_child())
        right_type = self.visit(node.right, scope.create_child())
        
        if left_type != NumberType() or right_type != NumberType():
            self.errors.append(INVALID_ARITHMETIC_OPERATION % (left_type.name, right_type.name)) 
            return ErrorType() 
        return NumberType()
        
    @visitor.when(StringOperationNode)
    def visit(self, node: StringOperationNode, scope: Scope = None):
        left_type = self.visit(node.left, scope.create_child())
        right_type = self.visit(node.right, scope.create_child())
        
        if left_type not in [StringType(), NumberType()] or right_type not in [StringType(), NumberType()]:
            self.errors.append(INVALID_STRING_OPERATION % (left_type.name, right_type.name))  
            return ErrorType()
        return StringType()
            
    @visitor.when(BooleanOperationNode)
    def visit(self, node: BooleanOperationNode, scope: Scope = None):
        left_type = self.visit(node.left, scope.create_child())
        right_type = self.visit(node.right, scope.create_child())
        
        if left_type != BooleanType() or right_type != BooleanType():
            self.errors.append(INVALID_BOOLEAN_OPERATION % (left_type.name, right_type.name))
            return ErrorType()
        return BooleanType()
    
    @visitor.when(NotNode)
    def visit(self, node: NotNode, scope: Scope = None):
        type = self.visit(node.node, scope.create_child())
        
        if type != BooleanType():
            self.errors.append(INVALID_NOT % type.name)
            return ErrorType()
        return BooleanType()
    
    @visitor.when(ComparisonOperationNode)
    def visit(self, node: ComparisonOperationNode, scope: Scope = None):
        left_type = self.visit(node.left, scope.create_child())
        right_type = self.visit(node.right, scope.create_child())
        
        if left_type != NumberType() or right_type != NumberType():
            self.errors.append(INVALID_COMPARISON_OPERATION % (left_type.name, right_type.name))
            return ErrorType()
        return BooleanType()
    
    @visitor.when(IsNode)
    def visit(self, node: IsNode, scope: Scope = None):
        self.visit(node.left, scope.create_child())
        
        try:
            self.context.get_type(node.right)
        except SemanticError as e:
            self.errors.append(e.text)
        
        return BooleanType()