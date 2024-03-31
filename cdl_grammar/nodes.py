from utils.ast import AtomicNode, UnaryNode, BinaryNode, Node
from automata_base import *
from cdl_grammar.chars import regular_chars, regex_grammar_extra_chars


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
    def __init__(self, left_lex: SymbolNode, right_lex: SymbolNode):
        self.lvalue = left_lex
        self.rvalue = right_lex

    def evaluate(self):
        print(self.lvalue)
        print(type(self.lvalue))
        l_ascii, r_ascii = ord(self.lvalue.lex), ord(self.rvalue.lex)
        aggregate = SymbolNode(self.lvalue).evaluate()

        for i in range(r_ascii - l_ascii + 1):
            aggregate = automata_union(aggregate, SymbolNode(chr(l_ascii + i)).evaluate())

        return aggregate
