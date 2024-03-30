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


def build_lr1_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])

    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    while pending:
        current = pending.pop()
        current_state = visited[current]

        for symbol in G.terminals + G.nonTerminals:
            item = current_state.state
            kernel = goto_lr1(item, symbol, just_kernel=True)
            if not kernel:
                continue
            try:
                next_state = visited[kernel]
            except KeyError:
                closure = goto_lr1(kernel, symbol, firsts)
                next_state = visited[kernel] = State(frozenset(closure), True)
                pending.append(kernel)

            current_state.add_transition(symbol.Name, next_state)

    automaton.set_formatter(multiline_formatter)
    return automaton


class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        grammar = self.G.AugmentedGrammar(True)

        if self.goto == {} or self.action == {}:
            pass
        else:
            return

        automaton = build_lr1_automaton(grammar)
        for i, node in enumerate(automaton):
            if self.verbose:
                print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == grammar.startSymbol:
                        self._register(self.action, (idx, grammar.EOF), (self.OK, None))
                    else:
                        for lookahead in item.lookaheads:
                            self._register(self.action, (idx, lookahead), (self.REDUCE, prod))
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        self._register(self.action, (idx, next_symbol),
                                       (self.SHIFT, node[next_symbol.Name][0].idx))
                    else:
                        self._register(self.goto, (idx, next_symbol), node[next_symbol.Name][0].idx)

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value


class Parser:
    def __init__(self, grammar):
        self.grammar = grammar

    def __call__(self):
        return Parser(self.grammar)
