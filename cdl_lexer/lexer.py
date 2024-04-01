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
    def __init__(self, table, eof):
        self.eof = eof
        print("build_regex start")
        self.regexs = _build_regexs(table)
        print("build_regex done")
        print("build_automaton start")
        self.automaton = self._build_automaton()
        print("build_automaton done")

    def _build_automaton(self):
        start = State('start')
        end = State('end', final=True)
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
                break

        return final, final_lex

    def _tokenize(self, text):
        while text:
            final, lex = self._walk(text)
            if final is None:
                yield lex, self.eof
                break
            yield lex, final.tag
            text = text[len(lex):]
        yield '$', self.eof

    def __call__(self, text):
        return [Token(lex, ttype) for lex, ttype in self._tokenize(text)]
