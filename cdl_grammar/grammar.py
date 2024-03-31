from cdl_reguex.regex import *
from utils.pycompiler import Grammar
from utils.utils import Token


def generate_regex_grammar():
    G = Grammar()

    regex = G.non_terminal('<regex>', startSymbol=True)
    branch, piece, atom, literal = G.non_terminals('<branch> <piece> <atom> <literal>')
    symbol, char_class_body, char_class_character = G.non_terminals('<symbol> <char-class-body> <char-class-character>')
    escape_comp = G.non_terminal("<escape-comp>")

    plus, star, question, bang = G.Terminals('+ * ? !')
    opar, cpar, obrack, cbrack = G.Terminals('( ) [ ]')
    dot, pipe, scape = G.Terminals('. | \\')
    literal_characters = G.Terminals(regular_chars)

    quotes = G.Terminals("\' \"")

    regex %= branch, lambda h, s: s[1]

    branch %= piece, lambda h, s: s[1]
    branch %= piece + branch, lambda h, s: ConcatNode(left=s[1], right=s[2])
    branch %= piece + pipe + branch, lambda h, s: UnionNode(left=s[1], right=s[3])

    piece %= atom, lambda h, s: s[1]
    piece %= atom + symbol, lambda h, s: s[2](child=s[1]),

    symbol %= plus, lambda h, s: PositiveClosureNode
    symbol %= star, lambda h, s: ClosureNode
    symbol %= question, lambda h, s: OptionalNode
    symbol %= bang, lambda h, s: NegationNode

    atom %= literal, lambda h, s: s[1]
    atom %= opar + branch + cpar, lambda h, s: s[2]
    atom %= obrack + char_class_body + cbrack, lambda h, s: s[2]

    whitespace = G.add_empty_space()
    literal %= whitespace, lambda h, s: SymbolNode(s[1])

    literal %= scape + escape_comp, lambda h, s: s[2]

    A = [x for x in G.terminals if x.Name == "A"][0]
    escape_comp %= A, lambda h, s: VocabularyNode()

    for v in literal_characters + quotes:
        literal %= v, lambda h, s: SymbolNode(s[1])

    for v in [plus, star, question, bang, opar, cpar, obrack, cbrack, pipe, dot, scape]:
        escape_comp %= v, lambda h, s: SymbolNode(s[1])

    for v in quotes:
        escape_comp %= v, lambda h, s: SymbolNode(s[1])

    char_class_body %= char_class_character, lambda h, s: s[1]
    char_class_body %= char_class_character + char_class_body, lambda h, s: ConcatNode(left=s[1], right=s[2])

    char_class_character %= literal, lambda h, s: s[1]
    char_class_character %= literal + dot + dot + literal, lambda h, s: RangeNode(s[1], s[4])

    return G


# This is for testing
G = generate_regex_grammar()
print("grammar generated")
parser = LR1Parser(G, verbose=False)
print("parser instantiate")
zero = [x for x in G.terminals if x.Name == '0'][0]
nine = [x for x in G.terminals if x.Name == '9'][0]
plus = [x for x in G.terminals if x.Name == '+'][0]
dot = [x for x in G.terminals if x.Name == '.'][0]
question = [x for x in G.terminals if x.Name == '?'][0]
asterisk = [x for x in G.terminals if x.Name == "*"][0]


obrack = [x for x in G.terminals if x.Name == '['][0]
opar = [x for x in G.terminals if x.Name == '('][0]
cpar = [x for x in G.terminals if x.Name == ')'][0]
cbrack = [x for x in G.terminals if x.Name == ']'][0]
pipe = [x for x in G.terminals if x.Name == '|'][0]

a = [x for x in G.terminals if x.Name == 'a'][0]
z = [x for x in G.terminals if x.Name == 'z'][0]
A = [x for x in G.terminals if x.Name == 'A'][0]
Z = [x for x in G.terminals if x.Name == 'Z'][0]
underscore = [x for x in G.terminals if x.Name == "_"][0]
whitespace = [x for x in G.terminals if x.Name == " "][0]
quotes = [x for x in G.terminals if x.Name == "\""][0]
scape = [x for x in G.terminals if x.Name == "\\"][0]

tokens = [quotes, opar, opar, scape, scape, scape, quotes, cpar, pipe, opar, scape, asterisk, cpar, cpar,
          asterisk, quotes, G.EOF]


regex = "\"((\\\\\\\")|(\\*))*\""
print(regex)
print(tokens)

derivation, operations = parser(tokens)

# print(derivation)

tokens = [Token(x.Name, x, 0) for x in tokens]
ast = evaluate_reverse_parse(derivation, operations, tokens)
ast.evaluate()

