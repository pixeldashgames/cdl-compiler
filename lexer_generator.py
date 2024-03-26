from automata import State
from regex import Regex
from utils import Token


# TODO: Fix the tag attribute in the State class when converting to DFA
class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()

    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            reg = Regex(regex)
            automaton = State.from_nfa(reg.automaton)
            for state in automaton:
                if state.final:
                    state.tag = (n,token_type)
            regexs.append(automaton)
        return regexs

    
    def _build_automaton(self):

        start = State('start')
        for regex in self.regexs:
            start.add_epsilon_transition(regex)

        return start.to_deterministic()
    
    def create(x:State):
        new_x = x
        new_x.tag = x.tag
        return new_x
    
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
        return [ Token(lex, ttype) for lex, ttype in self._tokenize(text) ]