from cdl_grammar.chars import regular_chars
from cdl_grammar.nodes import SymbolNode, ConcatNode, UnionNode, ClosureNode, PositiveClosureNode, \
    OptionalNode, NegationNode, VocabularyNode, RangeNode
from utils.pycompiler import Grammar


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
    piece %= atom + symbol, lambda h, s: s[2](s[1]),

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
