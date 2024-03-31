from automata_base import *
from cdl_parsing.parser import LR1Parser
from utils.evaluation import evaluate_reverse_parse
from utils.ast import AtomicNode, UnaryNode, BinaryNode, Node
from cdl_grammar.chars import *
from cdl_grammar.grammar import generate_regex_grammar
from utils.utils import Token


class SymbolNode(AtomicNode):
    def evaluate(self):
        return automata_symbol(self.lex)


class WildcardNode(AtomicNode):
    # TODO: create a automata_wildcard, to recognize any character
    def evaluate(self):
        pass


class VocabularyNode(Node):
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


class ConcatNode(BinaryNode):
    def evaluate(self):
        left = self.left.evaluate()
        right = self.right.evaluate()

        return automata_concatenation(left, right)


class RangeNode(Node):
    def __init__(self, left_lex, right_lex):
        self.lvalue = left_lex
        self.rvalue = right_lex

    def evaluate(self):
        l_ascii, r_ascii = ord(self.lvalue), ord(self.rvalue)
        aggregate = SymbolNode(self.lvalue).evaluate()

        for i in range(r_ascii - l_ascii + 1):
            aggregate = automata_union(aggregate, SymbolNode(chr(l_ascii + i)).evaluate())

        return aggregate


class Regex:

    def __init__(self, exp):
        self.grammar = generate_regex_grammar()
        self.parser = LR1Parser(self.grammar)
        self.automaton = self.build_regex(exp).evaluate()

    def build_regex(self, regex):
        tokens = []
        errors = []

        for i, c in enumerate(regex):
            token = [x for x in self.grammar.terminals if x.Name == c]
            if len(token) > 0:
                tokens.append(token[0])
            else:
                errors.append(f"Invalid character {c} on column {i}")

        tokens.append(self.grammar.EOF)
        derivation, operations = self.parser(tokens)
        tokens = [Token(x.Name, x) for x in tokens]
        ast = evaluate_reverse_parse(derivation, operations, tokens)
        return ast

