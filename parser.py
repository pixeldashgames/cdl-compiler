from utils.pycompiler import Grammar, Production, NonTerminal, Terminal, Epsilon
from ast import *


def grammar_init():
    g = Grammar()

    # TODO: Define the grammar for the parser
    # ------------------------------------------------
    # ------------------------------------------------
    return g


class Parser:
    def __init__(self, grammar):
        self.grammar = grammar

    def __call__(self):
        parser = Parser(self.grammar)
