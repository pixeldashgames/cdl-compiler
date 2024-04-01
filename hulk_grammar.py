from utils.pycompiler import Grammar
import hulk_ast as ast

# from cdl_parsing.parser import LR1Parser

HG = Grammar()

# No Terminales
program = HG.non_terminal('<program>', startSymbol=True)
entity_list, def_type, def_func, expr = HG.non_terminals('<entity-list> <def-class> <def-func> <expression>')
expr_list, param_list, arg_list = HG.non_terminals('<expr-list> <param-list> <arg-list>')
abst_expr_list, empty_expr_list = HG.non_terminals('<abst-expr-list> <empty-expr-list>')
abst_param_list, empty_param_list = HG.non_terminals('<abst-param-list> <empty-param-list>')
abst_arg_list, empty_arg_list = HG.non_terminals('<abst-arg-list> <empty-arg-list>')
param, arith, term, factor, atom, atrib = HG.non_terminals('<parameter> <arith> <term> <factor> <atom> <atrib>')
boolean, b_or, b_and, b_not, b_rel, prop = HG.non_terminals('<boolean> <ors> <ands> <nots> <relation> <proposition')
cond, loop, conct_expr, as_expr = HG.non_terminals('<conditional> <loop> <conct> <as-expr>')
func_call, meth_call, def_meth, def_attr = HG.non_terminals('<func-call> <meth-call> <def_meth> <def-attr>')
feature_list, abstract_feature_list, empty_feature_list = HG.non_terminals(
    '<feature-list> <abstract-feature-list> <empty-feature-list>')
asig_list, asig, des_asig = HG.non_terminals('<asig-list> <asig> <destructive-asig>')
if_cond, elif_cond, else_cond, elif_cond_list = HG.non_terminals('<if-cond> <elif-cond> <else-cond> <elif-cond-list>')

# Terminales

semi, colon, comma, dot, opar, cpar, ocur, ccur = HG.Terminals('; : , . ( ) { }')
equal, plus, minus, star, div, congr, conct, dconct, rarrow, dequal, power = HG.Terminals('= + - * / % @ @@ => := ^')
idx, let, new, fun, num, string, boolx, typex, inher, inx = HG.Terminals(
    'id let new function number string bool type inherits in')
minor, mayor, eminor, emayor, same, dif = HG.Terminals('< > <= >= == !=')
orx, andx, notx = HG.Terminals('| & !')
ifx, elsex, elifx = HG.Terminals('if else elif')
whilex, forx = HG.Terminals('while for')
isx, asx = HG.Terminals('is as')

# Producciones

program %= entity_list, lambda h, s: ast.ProgramNode(s[1])

entity_list %= def_type, lambda h, s: [s[1]]
entity_list %= def_type + entity_list, lambda h, s: [s[1]] + s[2]
entity_list %= def_func, lambda h, s: [s[1]]
entity_list %= def_func + entity_list, lambda h, s: [s[1]] + s[2]
entity_list %= expr + semi, lambda h, s: [[s[1]]]
entity_list %= ocur + abst_expr_list + ccur, lambda h, s: [s[2]]

def_type %= (typex + idx + opar + param_list + cpar + ocur + abstract_feature_list + ccur, lambda h,s:ast.TypeDeclarationNode(
    s[2], s[4], s[7], []))
def_type %= typex + idx + ocur + abstract_feature_list + ccur, lambda h, s: ast.TypeDeclarationNode(s[2], [], s[4], [])
def_type %= typex + idx + opar + param_list + cpar + inher + idx + ocur + abstract_feature_list + ccur, lambda h,s: ast.TypeDeclarationNode(
    s[2], s[4], s[9], [], s[7])
def_type %= typex + idx + inher + idx + ocur + abstract_feature_list + ccur, lambda h, s: ast.TypeDeclarationNode(s[2],[],s[6],[],s[4])
def_type %= typex + idx + opar + param_list + cpar + inher + idx + opar + abst_param_list + cpar + ocur + abstract_feature_list + ccur, lambda h, s: ast.TypeDeclarationNode(s[2], s[4], s[12], s[9], s[7])
def_type %= typex + idx + inher + idx + opar + abst_param_list + cpar + ocur + abstract_feature_list + ccur, lambda h,s: ast.TypeDeclarationNode(
    s[2], [], s[9], s[6], s[4])

abstract_feature_list %= feature_list, lambda h, s: s[1]
abstract_feature_list %= empty_feature_list, lambda h, s: s[1]

feature_list %= def_attr + semi, lambda h, s: [s[1]]
feature_list %= def_attr + semi + feature_list, lambda h, s: [s[1]] + s[3]
feature_list %= def_meth, lambda h, s: [s[1]]
feature_list %= def_meth + feature_list, lambda h, s: [s[1]] + s[2]

empty_feature_list %= HG.Epsilon, lambda h, s: []

def_attr %= idx + equal + expr + semi, lambda h, s: ast.AttrDeclarationNode(s[1], s[3])
def_attr %= idx + colon + idx + equal + expr + semi, lambda h, s: ast.AttrDeclarationNode(s[1], s[5], s[3])

def_meth %= idx + opar + abst_param_list + cpar + rarrow + expr + semi, lambda h, s: ast.MethDeclarationNode(s[1], s[3],
                                                                                                             [s[6]])
def_meth %= idx + opar + abst_param_list + cpar + ocur + abst_expr_list + ccur, lambda h, s: ast.MethDeclarationNode(
    s[1], s[3], s[6])
def_meth %= idx + opar + abst_param_list + cpar + colon + idx + rarrow + expr + semi, lambda h,s: ast.MethDeclarationNode(
    s[1], s[3], [s[8]], s[6])
def_meth %= idx + opar + abst_param_list + cpar + colon + idx + ocur + abst_expr_list + ccur, lambda h,s: ast.FuncDeclarationNode(
    s[1], s[3], s[8], s[6])

def_func %= fun + idx + opar + abst_param_list + cpar + rarrow + expr + semi, lambda h, s: ast.FuncDeclarationNode(s[2],s[4],[s[7]])
def_func %= fun + idx + opar + abst_param_list + cpar + ocur + abst_expr_list + ccur, lambda h,s: ast.FuncDeclarationNode(
    s[2], s[4], s[7])
def_func %= fun + idx + opar + abst_param_list + cpar + colon + idx + rarrow + expr + semi, lambda h,s: ast.FuncDeclarationNode(
    s[2], s[4], [s[9]], s[7])
def_func %= fun + idx + opar + abst_param_list + cpar + colon + idx + ocur + abst_expr_list + ccur, lambda h,s: ast.FuncDeclarationNode(
    s[2], s[4], s[9], s[7])

abst_param_list %= param_list, lambda h, s: s[1]
abst_param_list %= empty_param_list, lambda h, s: s[1]

param_list %= param, lambda h, s: [s[1]]
param_list %= param + comma + param_list, lambda h, s: [s[1]] + s[3]

empty_param_list %= HG.Epsilon, lambda h, s: []

param %= idx, lambda h, s: ast.ParamNode(s[1])
param %= idx + colon + idx, lambda h, s: ast.ParamNode(s[1], s[3])

abst_expr_list %= expr_list, lambda h, s: s[1]
abst_expr_list %= empty_expr_list, lambda h, s: s[1]

expr_list %= expr + semi, lambda h, s: [s[1]]
expr_list %= expr + semi + expr_list, lambda h, s: [s[1]] + s[3]

empty_expr_list %= HG.Epsilon, lambda h, s: []

# ...
expr %= let + asig_list + inx + expr, lambda h, s: ast.VarDeclarationNode(s[2], [s[4]])
expr %= let + asig_list + inx + ocur + abst_expr_list + ccur, lambda h, s: ast.VarDeclarationNode(s[2], s[5])
expr %= boolean, lambda h, s: s[1]
expr %= cond, lambda h, s: s[1]
expr %= loop, lambda h, s: s[1]
expr %= des_asig, lambda h, s: s[1]

des_asig %= idx + dequal + expr, lambda h, s: ast.DesAssignNode(s[1], s[3])
des_asig %= atrib + dequal + expr, lambda h, s: ast.DesAssignNode(s[1], s[3])

cond %= if_cond + elif_cond_list + else_cond, lambda h, s: ast.ConditionalNode([s[1]] + s[2] + [s[3]])
cond %= if_cond + else_cond, lambda h, s: ast.ConditionalNode([s[1]] + [s[3]])

elif_cond_list %= elif_cond + elif_cond_list, lambda h, s: [s[1]] + s[2]
elif_cond_list %= elif_cond, lambda h, s: [s[1]]

if_cond %= ifx + opar + expr + cpar + expr, lambda h, s: ast.IfNode(s[3], [s[5]])
if_cond %= ifx + opar + expr + cpar + ocur + abst_expr_list + ccur, lambda h, s: ast.IfNode(s[3], s[6])

else_cond %= elsex + expr, lambda h, s: ast.ElseNode([s[2]])
else_cond %= elsex + ocur + abst_expr_list + ccur, lambda h, s: ast.ElseNode(s[3])

elif_cond %= elifx + opar + expr + cpar + expr, lambda h, s: ast.ElifNode(s[3], [s[5]])
elif_cond %= elifx + opar + expr + cpar + ocur + abst_expr_list + ccur, lambda h, s: ast.ElifNode(s[3], s[6])

loop %= whilex + opar + expr + cpar + expr, lambda h, s: ast.WhileNode(s[3], [s[5]])
loop %= whilex + opar + expr + cpar + ocur + abst_expr_list + ccur, lambda h, s: ast.WhileNode(s[3], s[6])
loop %= forx + opar + idx + inx + expr + cpar + expr, lambda h, s: ast.ForNode(s[3], s[5], [s[7]])
loop %= forx + opar + idx + inx + expr + cpar + ocur + abst_expr_list + ccur, lambda h, s: ast.ForNode(s[3], s[5], s[8])

asig_list %= asig, lambda h, s: [s[1]]
asig_list %= asig + comma + asig_list, lambda h, s: [s[1]] + s[3]

asig %= idx + equal + expr, lambda h, s: ast.AssignNode(s[1], s[3])
asig %= idx + colon + idx + equal + expr, lambda h, s: ast.AssignNode(s[1], s[5], s[3])

boolean %= boolean + orx + b_or, lambda h, s: ast.OrNode(s[1], s[3])
boolean %= b_or, lambda h, s: s[1]

b_or %= b_or + andx + b_and, lambda h, s: ast.AndNode(s[1], s[3])
b_or %= b_and, lambda h, s: s[1]

b_and %= notx + b_and, lambda h, s: ast.NotNode(s[2])
b_and %= prop, lambda h, s: s[1]

prop %= b_not, lambda h, s: s[1]
prop %= prop + isx + idx, lambda h, s: ast.IsNode(s[1], s[3])

b_not %= b_not + minor + conct_expr, lambda h, s: ast.MinorNode(s[1], s[3])
b_not %= b_not + mayor + conct_expr, lambda h, s: ast.MayorNode(s[1], s[3])
b_not %= b_not + eminor + conct_expr, lambda h, s: ast.EqMinorNode(s[1], s[3])
b_not %= b_not + emayor + conct_expr, lambda h, s: ast.EqMayorNode(s[1], s[3])
b_not %= b_not + same + conct_expr, lambda h, s: ast.EqualNode(s[1], s[3])
b_not %= b_not + dif + conct_expr, lambda h, s: ast.DifferentNode(s[1], s[3])
b_not %= conct_expr, lambda h, s: s[1]

conct_expr %= arith, lambda h, s: s[1]
conct_expr %= conct_expr + conct + arith, lambda h, s: ast.ConcatenateNode(s[1], s[3])
conct_expr %= conct_expr + dconct + arith, lambda h, s: ast.DoubleConcatenateNode(s[1], s[3])

arith %= arith + plus + term, lambda h, s: ast.PlusNode(s[1], s[3])
arith %= arith + minus + term, lambda h, s: ast.MinusNode(s[1], s[3])
arith %= term, lambda h, s: s[1]

term %= term + star + factor, lambda h, s: ast.StarNode(s[1], s[3])
term %= term + div + factor, lambda h, s: ast.DivNode(s[1], s[3])
term %= term + congr + factor, lambda h, s: ast.CongruenceNode(s[1], s[3])
term %= factor, lambda h, s: s[1]

factor %= as_expr, lambda h, s: s[1]
factor %= as_expr + power + factor, lambda h, s: ast.PowerNode(s[1], s[3])
factor %= opar + arith + cpar, lambda h, s: s[2]

as_expr %= as_expr + asx + atom, lambda h, s: ast.AsNode(s[1], s[3])
as_expr %= atom, lambda h, s: s[1]

atom %= num, lambda h, s: ast.ConstantNumNode(s[1])
atom %= string, lambda h, s: ast.StringNode(s[1])
atom %= boolx, lambda h, s: ast.BoolNode(s[1])
atom %= idx, lambda h, s: ast.VariableNode(s[1])
atom %= atrib, lambda h, s: s[1]
atom %= func_call, lambda h, s: s[1]
atom %= meth_call, lambda h, s: s[1]
atom %= new + idx + opar + abst_arg_list + cpar, lambda h, s: ast.InstantiateNode(s[2], s[4])

atrib %= atom + dot + idx, lambda h, s: ast.AttributeNode(s[1] + s[3])

func_call %= idx + opar + abst_arg_list + cpar, lambda h, s: ast.FunCallNode(s[1], s[3])

meth_call %= atom + dot + idx + opar + abst_arg_list + cpar, lambda h, s: ast.MethCallNode(s[1], s[3], s[5])

des_asig %= idx + dequal + expr, lambda h, s: ast.DesAssignNode(s[1], s[3])

abst_arg_list %= arg_list, lambda h, s: s[1]
abst_arg_list %= empty_arg_list, lambda h, s: s[1]

arg_list %= expr, lambda h, s: [s[1]]
arg_list %= expr + comma + arg_list, lambda h, s: [s[1]] + s[3]

empty_arg_list %= HG.Epsilon, lambda h, s: []

# -------------------------------------------------------------------------------------------------------------------------------------
# parser = LR1Parser(HG)
# print("Terrible.♠")

