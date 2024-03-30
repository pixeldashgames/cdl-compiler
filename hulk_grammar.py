from utils.pycompiler import Grammar

HG = Grammar()

# No Terminales
program = HG.NonTerminal('<program>', startSymbol=True)
entity_list, def_type, def_func, expr = HG.NonTerminal('<entity-list> <def-class> <def-func> <expression>')
expr_list, param_list, arg_list = HG.NonTerminal('<expr-list> <param-list> <arg-list>')
abst_expr_list, empty_expr_list = HG.NonTerminal('<abst-expr-list> <empty-expr-list>')
abst_param_list, empty_param_list = HG.NonTerminal('<abst-param-list> <empty-param-list>')
abst_arg_list, empty_arg_list = HG.NonTerminal('<abst-arg-list> <empty-arg-list>')
param, arith, term, factor, atom, boolean = HG.NonTerminals('<parameter> <arith> <term> <factor> <atom>')
boolean, b_or, b_and, b_not, b_rel = HG.NonTerminals('<boolean> <ors> <ands> <nots> <relation>')
cond, loop = HG.NonTerminal('<conditional> <loop>')
func_call, def_meth, def_attr = HG.NonTerminal('<func-call> <def_meth> <def-attr>')
feature_list, abstract_feature_list, empty_feature_list= HG.NonTerminal('<feature-list> <abstract-feature-list> <empty-feature-list>')
asig_list, asig, des_asig= HG.NonTerminals('<asig-list> <asig> <destructive-asig>')

# Terminales

semi, colon, comma, dot, opar, cpar, ocur, ccur = HG.Terminals('; : , . ( ) { }')
equal, plus, minus, star, div, congr, conct, dconct, rarrow, dequal = HG.Terminals('= + - * / % @ @@ => :=')
idx, let, new, fun, num, string, typex, inher, inx  = HG.Terminals('id let new function number string type inherits in')
true, false = HG.Terminals('true, false')
minor, mayor, eminor, emayor, same, dif = HG.Terminals('< > <= >= == !=')
orx, andx, notx = HG.Terminals('| & !')
ifx, elesex, elifx = HG.Terminals('if else elif')
whilex, forx = HG.Terminals('while for')


# Producciones

program %= entity_list

entity_list %= def_type
entity_list %= def_type + entity_list
entity_list %= def_func
entity_list %= def_func + entity_list
entity_list %= expr + semi
entity_list %= expr + semi + entity_list

def_type %= typex + idx + ocur + abstract_feature_list + ccur
def_type %= typex + idx + inher + idx + ocur + abstract_feature_list + ccur

abstract_feature_list %= feature_list
abstract_feature_list %= empty_feature_list

feature_list %= def_attr + semi
feature_list %= def_attr + semi + feature_list
feature_list %= def_meth
feature_list %= def_meth + feature_list

empty_feature_list %= HG.Epsilon

def_attr %= idx + equal + expr
def_attr %= idx + colon + idx + equal + expr

def_func %= fun + idx + opar + abst_param_list + cpar + rarrow + expr + semi
def_func %= fun + idx + opar + abst_param_list + cpar + ocur + abst_expr_list + ccur
def_func %= fun + idx + opar + abst_param_list + cpar + colon + idx + rarrow + expr + semi
def_func %= fun + idx + opar + abst_param_list + cpar + colon + idx + ocur + abst_expr_list + ccur

abst_param_list %= param_list
abst_param_list %= empty_param_list

param_list %= param
param_list %= param + comma + param_list

empty_param_list %= HG.Epsilon

param %= idx
param %= idx + colon + idx

abst_expr_list %= expr_list
abst_expr_list %= empty_expr_list

expr_list %= expr + semi
expr_list %= expr + semi + expr_list

empty_expr_list %= HG.Epsilon

# ...
expr %= let + asig_list + inx + expr + semi
expr %= let + asig_list + inx + ocur + abst_expr_list + ccur
expr %= arith
expr %= boolean
expr %= cond
expr %= loop

cond %= ifx + opar + boolean + cpar + colon + expr + semi
cond %= ifx + opar + boolean + cpar + colon + ocur + abst_expr_list + ccur
cond %= elifx + opar + boolean + cpar + colon + expr + semi
cond %= elifx + opar + boolean + cpar + colon + ocur + abst_expr_list + ccur
cond %= elifx + colon + expr + semi
cond %= elifx + colon + ocur + abst_expr_list + ccur

loop %= whilex + opar + boolean + cpar + expr + semi
loop %= whilex + opar + boolean + cpar + ocur + abst_expr_list + ccur
loop %= forx + opar + idx + inx + expr + cpar + expr + semi
loop %= forx + opar + idx + inx + expr + cpar + ocur + abst_expr_list + ccur

asig_list %= asig
asig_list %= asig + comma + asig_list

asig %= idx + equal + expr
asig %= idx + colon + idx + equal + expr

arith %= arith + plus + term
arith %= arith + minus + term
arith %= term

term %= term + star + factor
term %= term + div + factor
term %= term + congr + factor
term %= factor

factor %= atom
factor %= opar + arith + cpar

boolean %= boolean + orx + b_or
boolean %= b_or

b_or %= b_or + andx + b_and
b_or %= b_and

b_and %= notx + b_not
b_and %= b_not

b_not %= atom + minor + atom
b_not %= atom + mayor + atom
b_not %= atom + eminor + atom
b_not %= atom + emayor + atom
b_not %= atom + same + atom
b_not %= atom + dif + atom
b_not %= atom
b_not %= opar + boolean + cpar

atom %= num
atom %= string
atom %= idx
atom %= func_call
atom %= new + idx + opar + cpar
atom %= true
atom %= false
atom %= des_asig
atom %= string + conct + expr
atom %= string + dconct + expr

func_call %= atom + dot + idx + opar + abst_arg_list + cpar

des_asig %= idx + dequal + expr

abst_arg_list %= arg_list
abst_arg_list %= empty_arg_list

arg_list %= expr
arg_list %= expr + comma + arg_list

empty_arg_list %= HG.Epsilon