from automata_base import *
from cdl_parsing.parser import LR1Parser
from utils.evaluation import evaluate_reverse_parse
from cdl_grammar.nodes import Node
from utils.utils import Token
from cdl_grammar.grammar import generate_regex_grammar


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
        ast: Node = evaluate_reverse_parse(derivation, operations, tokens)
        return ast

