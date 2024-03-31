from utils.pycompiler import Grammar
import hulk_ast as ast
#from Parsing.parser import LR1Parser

HG = Grammar()

# No Terminales
program = HG.NonTerminal('<program>', startSymbol=True)
entity_list, def_type, def_func, expr = HG.NonTerminals('<entity-list> <def-class> <def-func> <expression>')
expr_list, param_list, arg_list = HG.NonTerminals('<expr-list> <param-list> <arg-list>')
abst_expr_list, empty_expr_list = HG.NonTerminals('<abst-expr-list> <empty-expr-list>')
abst_param_list, empty_param_list = HG.NonTerminals('<abst-param-list> <empty-param-list>')
abst_arg_list, empty_arg_list = HG.NonTerminals('<abst-arg-list> <empty-arg-list>')
param, arith, term, factor, atom = HG.NonTerminals('<parameter> <arith> <term> <factor> <atom>')
boolean, b_or, b_and, b_not, b_rel = HG.NonTerminals('<boolean> <ors> <ands> <nots> <relation>')
cond, loop = HG.NonTerminals('<conditional> <loop>')
func_call, meth_call, def_meth, def_attr = HG.NonTerminals('<func-call> <meth-call> <def_meth> <def-attr>')
feature_list, abstract_feature_list, empty_feature_list= HG.NonTerminals('<feature-list> <abstract-feature-list> <empty-feature-list>')
asig_list, asig, des_asig= HG.NonTerminals('<asig-list> <asig> <destructive-asig>')

# Terminales

semi, colon, comma, dot, opar, cpar, ocur, ccur = HG.Terminals('; : , . ( ) { }')
equal, plus, minus, star, div, congr, conct, dconct, rarrow, dequal = HG.Terminals('= + - * / % @ @@ => :=')
idx, let, new, fun, num, string, boolx, typex, inher, inx  = HG.Terminals('id let new function number string bool type inherits in')
minor, mayor, eminor, emayor, same, dif = HG.Terminals('< > <= >= == !=')
orx, andx, notx = HG.Terminals('| & !')
ifx, elsex, elifx = HG.Terminals('if else elif')
whilex, forx = HG.Terminals('while for')
isx, asx = HG.Terminals('is as')


# Producciones

program %= entity_list, lambda h,s: ast.ProgramNode(s[1])

entity_list %= def_type, lambda h,s: [s[1]]
entity_list %= def_type + entity_list, lambda h,s: [s[1]] + s[2]
entity_list %= def_func, lambda h,s: [s[1]]
entity_list %= def_func + entity_list, lambda h,s: [s[1]] + s[2]
entity_list %= expr + semi, lambda h,s: [s[1]]
entity_list %= ocur + abst_expr_list + ccur, lambda h,s: [s[2]]

def_type %= typex + idx + opar + abst_param_list + cpar + ocur + abstract_feature_list + ccur, lambda h,s: ast.TypeDeclarationNode(s[2], s[4], s[7])
def_type %= typex + idx + inher + idx + opar + abst_param_list + cpar + ocur + abstract_feature_list + ccur, lambda h,s: ast.TypeDeclarationNode(s[2], s[6], s[9], s[4] )

abstract_feature_list %= feature_list, lambda h,s: s[1]
abstract_feature_list %= empty_feature_list, lambda h,s: s[1]

feature_list %= def_attr + semi, lambda h,s: [s[1]]
feature_list %= def_attr + semi + feature_list, lambda h,s: [s[1]] + s[3]
feature_list %= def_meth, lambda h,s: [s[1]]
feature_list %= def_meth + feature_list, lambda h,s: [s[1]] + s[2]

empty_feature_list %= HG.Epsilon, lambda h,s: []

def_attr %= idx + equal + expr, lambda h,s: ast.AttrDeclarationNode(s[1], s[3])
def_attr %= idx + colon + idx + equal + expr, lambda h,s: ast.AttrDeclarationNode(s[1], s[5], s[3])

def_meth %= idx + opar + abst_param_list + cpar + rarrow + expr + semi, lambda h,s: ast.MethDeclarationNode(s[1], s[3], s[6])
def_meth %= idx + opar + abst_param_list + cpar + ocur + abst_expr_list + ccur, lambda h,s: ast.MethDeclarationNode(s[1], s[3], s[6])
def_meth %= idx + opar + abst_param_list + cpar + colon + idx + rarrow + expr + semi, lambda h,s: ast.MethDeclarationNode(s[1], s[3], s[8], s[6])
def_meth %= idx + opar + abst_param_list + cpar + colon + idx + ocur + abst_expr_list + ccur, lambda h,s: ast.FuncDeclarationNode(s[1], s[3], s[8], s[6])

def_func %= fun + idx + opar + abst_param_list + cpar + rarrow + expr + semi, lambda h,s: ast.FuncDeclarationNode(s[2], s[4], s[7])
def_func %= fun + idx + opar + abst_param_list + cpar + ocur + abst_expr_list + ccur, lambda h,s: ast.FuncDeclarationNode(s[2], s[4], s[7])
def_func %= fun + idx + opar + abst_param_list + cpar + colon + idx + rarrow + expr + semi, lambda h,s: ast.FuncDeclarationNode(s[2], s[4], s[9], s[7])
def_func %= fun + idx + opar + abst_param_list + cpar + colon + idx + ocur + abst_expr_list + ccur, lambda h,s: ast.FuncDeclarationNode(s[2], s[4], s[9], s[7])

abst_param_list %= param_list, lambda h,s: s[1]
abst_param_list %= empty_param_list, lambda h,s: s[1]

param_list %= param, lambda h,s: [s[1]]
param_list %= param + comma + param_list, lambda h,s: [s[1]] + s[3]

empty_param_list %= HG.Epsilon, lambda h,s: []

param %= idx, lambda h,s: ast.ParamNode(s[1])
param %= idx + colon + idx, lambda h,s: ast.ParamNode(s[1], s[3])

abst_expr_list %= expr_list, lambda h,s: s[1]
abst_expr_list %= empty_expr_list, lambda h,s: s[1]

expr_list %= expr + semi, lambda h,s: [s[1]]
expr_list %= expr + semi + expr_list, lambda h,s: [s[1]] + s[3]

empty_expr_list %= HG.Epsilon, lambda h,s: []

# ...
expr %= let + asig_list + inx + expr + semi, lambda h,s: ast.VarDeclarationNode(s[2], s[4])
expr %= let + asig_list + inx + ocur + abst_expr_list + ccur, lambda h,s: ast.VarDeclarationNode(s[2], s[5])
expr %= arith, lambda h,s: s[1]
expr %= boolean, lambda h,s: s[1]
expr %= cond, lambda h,s: s[1]
expr %= loop, lambda h,s: s[1]
expr %= expr + asx + idx, lambda h,s: ast.AsNode(s[1], s[3])
atom %= expr + conct + expr, lambda h,s: ast.ConcatenateNode(s[1], s[3])
atom %= expr + dconct + expr, lambda h,s: ast.DoubleConcatenateNode(s[1], s[3])

cond %= ifx + opar + boolean + cpar + expr + semi, lambda h,s: ast.IfNode(s[3], s[5])
cond %= ifx + opar + boolean + cpar + ocur + abst_expr_list + ccur, lambda h,s: ast.IfNode(s[3], s[6])
cond %= elifx + opar + boolean + cpar + expr + semi, lambda h,s: ast.ElifNode(s[3], s[5])
cond %= elifx + opar + boolean + cpar + ocur + abst_expr_list + ccur, lambda h,s: ast.ElifNode(s[3], s[6])
cond %= elsex + expr + semi, lambda h,s: ast.ElseNode(s[2])
cond %= elsex + ocur + abst_expr_list + ccur, lambda h,s: ast.ElseNode(s[3])

loop %= whilex + opar + boolean + cpar + expr + semi, lambda h,s: ast.WhileNode(s[3], s[5])
loop %= whilex + opar + boolean + cpar + ocur + abst_expr_list + ccur, lambda h,s: ast.WhileNode(s[3], s[6])
loop %= forx + opar + idx + inx + expr + cpar + expr + semi, lambda h,s: ast.ForNode(s[3], s[5], s[7])
loop %= forx + opar + idx + inx + expr + cpar + ocur + abst_expr_list + ccur, lambda h,s: ast.ForNode(s[3], s[5], s[8])

asig_list %= asig, lambda h,s: [s[1]]
asig_list %= asig + comma + asig_list, lambda h,s: [s[1]] + s[3]

asig %= idx + equal + expr, lambda h,s: ast.AssignNode(s[1], s[3])
asig %= idx + colon + idx + equal + expr, lambda h,s: ast.AssignNode(s[1], s[5], s[3])

arith %= arith + plus + term, lambda h,s: ast.PlusNode(s[1], s[3])
arith %= arith + minus + term, lambda h,s: ast.PlusNode(s[1], s[3])
arith %= term, lambda h,s: s[1]

term %= term + star + factor, lambda h,s: ast.StarNode(s[1], s[3])
term %= term + div + factor, lambda h,s: ast.DivNode(s[1], s[3])
term %= term + congr + factor, lambda h,s: ast.CongruenceNode(s[1], s[3])
term %= factor, lambda h,s: s[1]

factor %= atom, lambda h,s: s[1]
factor %= opar + arith + cpar, lambda h,s: s[2]

boolean %= boolean + orx + b_or, lambda h,s: ast.OrNode(s[1], s[3])
boolean %= b_or, lambda h,s: s[1]

b_or %= b_or + andx + b_and, lambda h,s: ast.AndNode(s[1], s[3])
b_or %= b_and, lambda h,s: s[1]

b_and %= notx + b_not, lambda h,s: ast.NotNode(s[2])
b_and %= b_not, lambda h,s: s[1]

b_not %= expr + minor + expr, lambda h,s: ast.MinorNode(s[1], s[3])
b_not %= expr + mayor + expr, lambda h,s: ast.MayorNode(s[1], s[3])
b_not %= expr + eminor + expr, lambda h,s: ast.EqMinorNode(s[1], s[3])
b_not %= expr + emayor + expr, lambda h,s: ast.EqMayorNode(s[1], s[3])
b_not %= expr + same + expr, lambda h,s: ast.EqualNode(s[1], s[3])
b_not %= expr + dif + expr, lambda h,s: ast.DifferentNode(s[1], s[3])
b_not %= atom, lambda h,s: s[1]
b_not %= opar + boolean + cpar, lambda h,s: s[2]
b_not %= expr + isx + idx, lambda h,s: ast.IsNode(s[1], s[3])

atom %= num, lambda h,s: ast.ConstantNumNode(s[1])
atom %= string, lambda h,s: ast.StringNode(s[1])
atom %= boolx, lambda h,s: ast.BoolNode(s[1])
atom %= idx, lambda h,s: ast.VariableNode(s[1])
atom %= func_call, lambda h,s: s[1]
atom %= meth_call, lambda h,s: s[1]
atom %= new + idx + opar + cpar, lambda h,s: ast.InstantiateNode(s[2])
atom %= des_asig, lambda h,s: s[1]

func_call %= idx + opar + abst_arg_list + cpar, lambda h,s: ast.FunCallNode(s[1], s[3])

meth_call %= atom + dot + idx + opar + abst_arg_list + cpar, lambda h,s: ast.MethCallNode(s[1], s[3], s[5])

des_asig %= idx + dequal + expr, lambda h,s: ast.DesAssignNode(s[1], s[3])

abst_arg_list %= arg_list, lambda h,s: s[1]
abst_arg_list %= empty_arg_list, lambda h,s: s[1]

arg_list %= expr, lambda h,s: [s[1]]
arg_list %= expr + comma + arg_list, lambda h,s: [s[1]] + s[3]

empty_arg_list %= HG.Epsilon, lambda h,s: []

# -------------------------------------------------------------------------------------------------------------------------------------
#parser = LR1Parser(HG)
#print("Terrible.♠")