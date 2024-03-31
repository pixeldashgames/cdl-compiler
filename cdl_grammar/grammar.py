from cdl_reguex.regex import *
from utils.pycompiler import Grammar


def generate_regex_grammar():
    grammar = Grammar()

    reg_expr, sequence, unit, element, literal_val = grammar.non_terminals('<reg_expr> <sequence> <unit> <element> '
                                                                           '<literal_val>')
    symbol, class_body, class_char = grammar.non_terminals('<symbol> <class_body> <class_char>')
    escape_sequence = grammar.non_terminals("<escape_sequence>")

    plus_op, star_op, question_op, not_op = grammar.terminals('+ * ? !')
    open_par, close_par, open_bracket, close_bracket = grammar.terminals('( ) [ ]')
    dot_op, pipe_op, escape_char = grammar.terminals('. | \\')
    literal_chars = grammar.terminals()

    quote_chars = grammar.terminals("\' \"")

    reg_expr %= sequence, lambda h, s: s[1]

    sequence %= unit, lambda h, s: s[1]
    sequence %= unit + sequence, lambda h, s: ConcatNode(s[1], s[2])
    sequence %= unit + pipe_op + sequence, lambda h, s: UnionNode(s[1], s[3])

    unit %= element, lambda h, s: s[1]
    unit %= element + symbol, lambda h, s: s[2](child=s[1]),

    symbol %= plus_op, lambda h, s: PositiveClosureNode
    symbol %= star_op, lambda h, s: ClosureNode
    symbol %= question_op, lambda h, s: OptionalNode
    symbol %= not_op, lambda h, s: NegationNode

    element %= literal_val, lambda h, s: s[1]
    element %= open_par + sequence + close_par, lambda h, s: s[2]
    element %= open_bracket + class_body + close_bracket, lambda h, s: s[2]

    space_char = grammar.add_empty_space()
    literal_val %= space_char, lambda h, s: SymbolNode(s[1])

    literal_val %= escape_char + escape_sequence, lambda h, s: s[2]

    A_terminal = [x for x in grammar.terminals if x.Name == "A"][0]
    escape_sequence %= A_terminal, lambda h, s: VocabularyNode()

    for v in literal_chars + quote_chars:
        literal_val %= v, lambda h, s: SymbolNode(s[1])

    for v in [plus_op, star_op, question_op, not_op, open_par, close_par, open_bracket, close_bracket, pipe_op, dot_op, escape_char]:
        escape_sequence %= v, lambda h, s: SymbolNode(s[1])

    for v in quote_chars:
        escape_sequence %= v, lambda h, s: SymbolNode(s[1])

    class_body %= class_char, lambda h, s: s[1]
    class_body %= class_char + class_body, lambda h, s: ConcatNode(s[1], s[2])

    class_char %= literal_val, lambda h, s: s[1]
    class_char %= literal_val + dot_op + dot_op + literal_val, lambda h, s: RangeNode(s[1], s[4])

    return grammar
