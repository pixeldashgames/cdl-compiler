from automata_base import NFA, DFA, nfa_to_dfa
from automata_base import *
from utils.pycompiler import Grammar
from utils.utils import Token
from parser import LR1Parser
from utils.evaluation import evaluate_reverse_parse
from utils.ast import AtomicNode, UnaryNode, BinaryNode, Node
from utils.chars import *


class SymbolNode(AtomicNode):
    def evaluate(self):
        return automata_symbol(self.lex)


SymbolNode('a').evaluate()


class VocabularyNode(AtomicNode):
    def evaluate(self):
        chars = regular_chars.split()
        automata1 = SymbolNode(chars[0]).evaluate()
        automata2 = SymbolNode(chars[1]).evaluate()
        union = automata_union(automata1, automata2)

        for char in chars[2:]:
            automata = SymbolNode(char).evaluate()
            union = automata_union(union, automata)
        for char in regex_grammar_extra_chars:
            automata = SymbolNode(char).evaluate()
            union = automata_union(union, automata)

        result = automata_union(union, SymbolNode(' ').evaluate())

        return automata_minimization(nfa_to_dfa(result))


class ClosureNode(UnaryNode):
    def evaluate(self):
        return automata_closure(self.node.evaluate())


ClosureNode(SymbolNode('a')).evaluate()


class PositiveClosureNode(UnaryNode):
    def evaluate(self):
        return automata_positive_closure(self.node.evaluate())


class OptionalNode(UnaryNode):
    def evaluate(self):
        return automata_optional(self.node.evaluate())


class NegationNode(UnaryNode):
    def evaluate(self):
        return automata_negation(self.node.evaluate())


class UnionNode(BinaryNode):
    def evaluate(self):
        left = self.left.evaluate()
        right = self.right.evaluate()

        return automata_union(left, right)


UnionNode(SymbolNode('a'), SymbolNode('b')).evaluate()


class ConcatNode(BinaryNode):
    def evaluate(self):
        left = self.left.evaluate()
        right = self.right.evaluate()

        return automata_concatenation(left, right)


ConcatNode(SymbolNode('a'), SymbolNode('b')).evaluate()


class RangeNode(Node):
    def __init__(self, left_lex, right_lex) -> None:
        self.lvalue = left_lex
        self.rvalue = right_lex

    def evaluate(self):
        lascii, rascii = ord(self.lvalue), ord(self.rvalue)
        aggregate = SymbolNode(self.lvalue).evaluate()

        for i in range(rascii - lascii + 1):
            aggregate = automata_union(aggregate, SymbolNode(chr(lascii + i)).evaluate())

        return aggregate


RangeNode(SymbolNode('a'), SymbolNode('z')).evaluate()

G = Grammar()

E = G.non_terminal('E', True)
T, F, A = G.non_terminals('T F A')
pipe, star, opar, cpar, symbol, epsilon = G.terminals('| * ( ) symbol ε')

E %= E + pipe + T, lambda s: UnionNode(s[1], s[3])
E %= T, lambda s: s[1]

T %= T + F, lambda s: ConcatNode(s[1], s[2])
T %= F, lambda s: s[1]

F %= A + star, lambda s: ClosureNode(s[1])
F %= A, lambda s: s[1]

A %= symbol, lambda s: SymbolNode(s[1])
A %= epsilon, lambda s: EpsilonNode(s[1])
A %= opar + E + cpar, lambda s: s[2]


def regex_tokenizer(text, G, skip_whitespaces=True):
    tokens = []

    for char in text:
        if skip_whitespaces and char.isspace():
            continue
        elif char == "|":
            tokens.append(Token("|", pipe))
        elif char == "*":
            tokens.append(Token("*", star))
        elif char == "(":
            tokens.append(Token("(", opar))
        elif char == ")":
            tokens.append(Token(")", cpar))
        elif char == "ε":
            tokens.append(Token("ε", epsilon))

        else:
            tokens.append(Token(char, symbol))

    tokens.append(Token('$', G.EOF))
    return tokens


class Regex:

    def __init__(self, exp):
        self.exp = exp

    def automaton(self):
        tokens = regex_tokenizer(self, G)
        parser = LR1Parser(G)
        parse, operations = parser([t.token_type for t in tokens])
        ast = evaluate_reverse_parse(parse, operations, tokens)

        nfa = ast.evaluate()
        dfa = nfa_to_dfa(nfa)
        mini = automata_minimization(dfa)

        return mini
