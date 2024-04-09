from utils.automata import State
from cdl_reguex.regex import Regex
from utils.utils import Token


def _build_regexs(table):
    regexs = []
    for n, (token_type, regex) in enumerate(table):

        states = State.from_nfa(Regex(regex).automaton)
        for state in states:
            if state.final:
                state.tag = (n, token_type)
        regexs.append(states)
    return regexs


class Lexer:
    def __init__(self, table, eof, verbose = False):
        self.eof = eof
        if verbose:
            print("build_regex start")
        self.regexs = _build_regexs(table)
        if verbose:
            print("build_regex done")
        if verbose:
            print("build_automaton start")
        self.automaton = self._build_automaton()
        if verbose:
            print("build_automaton done")

    def _build_automaton(self):
        start = State('start')
        for regex in self.regexs:
            start.add_epsilon_transition(regex)
        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex = ''

        for symbol in string:
            if symbol in state.transitions:
                state = state.transitions[symbol][0]
                lex += symbol
                if state.final:
                    final = state
                    final_lex = lex
            else:
                if final_lex == '':
                    print("breaking at", symbol)
                break

        return final, final_lex

    def _tokenize(self, text):
        line = 1
        while text:
            for c in text:
                if not c.isspace():
                    break
                if c == '\n':
                    line += 1
            text = text.lstrip()
            final, lex = self._walk(text)
            if final is None:
                print(final,"-><-", lex, "-><-", text)
                break
            final_tag = min(final.tag, key=lambda x: x[0])
            yield lex, final_tag[1], line
            text = text[len(lex):]
        yield '$', self.eof, line

    def __call__(self, text):
        return [Token(lex, ttype, line) for lex, ttype, line in self._tokenize(text)]
