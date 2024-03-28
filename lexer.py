from utils.automata import State

from utils.utils import Token


class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()

    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):

            states = State.from_nfa(Regex(regex).automaton())
            for state in states:
                if state.final:
                    state.tag = (n, token_type)
            regexs.append(states)
        return regexs

    def _build_automaton(self):
        start = State('start')
        end = State('end', True)
        for regex in self.regexs:
            start.add_epsilon_transition(regex)

        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex = ''

        for symbol in string:
            if symbol in state.transitions:
                state[0] = state.transitions[symbol]
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


# ----------------------------------------------------------------------------------
# Test
# ----------------------------------------------------------------------------------

nonzero_digits = '|'.join(str(n) for n in range(1, 10))
letters = '|'.join(chr(n) for n in range(ord('a'), ord('z') + 1))

print('Non-zero digits:', nonzero_digits)
print('Letters:', letters)

lexer = Lexer([
    ('num', f'({nonzero_digits})(0|{nonzero_digits})*'),
    ('for', 'for'),
    ('foreach', 'foreach'),
    ('space', '  *'),
    ('id', f'({letters})({letters}|0|{nonzero_digits})*')
], 'eof')

text = '5465 for 45foreach fore'
print(f'\n>>> Tokenizando: "{text}"')
tokens = lexer(text)
print(tokens)
assert [t.token_type for t in tokens] == ['num', 'space', 'for', 'space', 'num', 'foreach', 'space', 'id', 'eof']
assert [t.lex for t in tokens] == ['5465', ' ', 'for', ' ', '45', 'foreach', ' ', 'fore', '$']

text = '4forense forforeach for4foreach foreach 4for'
print(f'\n>>> Tokenizando: "{text}"')
tokens = lexer(text)
print(tokens)
assert [t.token_type for t in tokens] == ['num', 'id', 'space', 'id', 'space', 'id', 'space', 'foreach', 'space', 'num',
                                          'for', 'eof']
assert [t.lex for t in tokens] == ['4', 'forense', ' ', 'forforeach', ' ', 'for4foreach', ' ', 'foreach', ' ', '4',
                                   'for', '$']
