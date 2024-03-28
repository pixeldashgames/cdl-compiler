from shift_reduce import ShiftReduceParser
from utils.pycompiler import Item
from utils.automata import State, multiline_formatter
from utils.pycompiler import Grammar, Production, NonTerminal, Terminal, Epsilon
from pending.utils import *


def grammar_init():
    g = Grammar()

    # TODO: Define the grammar for the parser
    # ------------------------------------------------
    # ------------------------------------------------
    return g


def build_automaton_for_lr1_parser(grammar):
    assert len(grammar.startSymbol.productions) == 1, "Grammar must be augmented"

    firsts = compute_firsts(grammar)
    firsts[grammar.EOF] = ContainerSet(grammar.EOF)

    start_production = grammar.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(grammar.EOF,))
    start = frozenset([start_item])

    closure = closure_for_lr1(start, firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    while pending:
        current = pending.pop()
        current_state = visited[current]

        for symbol in grammar.terminals + grammar.nonTerminals:
            items = current_state.state
            kernel = goto_for_lr1(items, symbol, just_kernel=True)
            if not kernel:
                continue
            try:
                next_state = visited[kernel]
            except KeyError:
                closure = goto_for_lr1(items, symbol, firsts)
                next_state = visited[kernel] = State(frozenset(closure), True)
                pending.append(kernel)

            current_state.add_transition(symbol.Name, next_state)

    automaton.set_formatter(lambda x: "")
    return automaton


class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        g = self.G.AugmentedGrammar(True)

        automaton = build_automaton_for_lr1_parser(g)
        for i, node in enumerate(automaton):
            if self.verbose:
                print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == g.startSymbol:
                        self.add(self.action, (idx, g.EOF), ("OK", None))
                    else:
                        for lookahead in item.lookaheads:
                            self.add(self.action, (idx, lookahead), ("REDUCE", prod))
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        self.add(self.action, (idx, next_symbol),
                                 ("SHIFT", node[next_symbol.Name][0].idx))
                    else:
                        self.add(self.goto, (idx, next_symbol), node[next_symbol.Name][0].idx)

    @staticmethod
    def add(table, key, value):
        assert key not in table or table[key] == value, f'Conflict {key} {table[key]} {value}'
        table[key] = value

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value


class Parser:
    def __init__(self, grammar):
        self.grammar = grammar

    def __call__(self):
        parser = Parser(self.grammar)
