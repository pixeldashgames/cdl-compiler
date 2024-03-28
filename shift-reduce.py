from utils.automata import State
from utils.pycompiler import (Grammar, Item, SintacticException)
from utils.utils import (ContainerSet, EOF)

from pandas import DataFrame


class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __init__(self, G: Grammar, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()

    def _build_parsing_table(self):
        raise NotImplementedError()

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value

    def __call__(self, w):
        stack = [0]
        cursor = 0
        output = []
        operations = []
        count = 1
        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, '<---||--->', w[cursor:], count)
            count += 1

            lookahead = lookahead.token_type.Name
            if (state, lookahead) not in self.action.keys():
                ##########################TODO###########################
                # Mejorar la informacion al detectar error en la cadena #
                #########################################################
                desire = ''
                for (state_d, lookahead_d) in self.action.keys():
                    if state_d == state:
                        desire += f"- '{lookahead_d}'\n"

                token = w[cursor]
                err = f'No se puede parsear la cadena. No se esperaba un token {lookahead} '
                err += f'en la linea {token.row} y columna {token.col}.\n'
                if len(desire) > 0:
                    err += 'Se esperaba:\n'
                    err += desire
                raise SintacticException(err)

            action, tag = self.action[state, lookahead]

            # SHIFT
            if action == ShiftReduceParser.SHIFT:
                stack.append(lookahead)
                stack.append(tag)
                operations.append(ShiftReduceParser.SHIFT)
                cursor += 1

            # REDUCE
            elif action == ShiftReduceParser.REDUCE:
                left, right = production = self.G.Productions[tag]
                count_delete = 2 * len(right)
                for i in range(count_delete):
                    stack.pop()
                new_state = self.goto[stack[-1], left.Name]
                stack.append(left.Name)
                stack.append(new_state)
                output.append(production)
                operations.append(ShiftReduceParser.REDUCE)

            # ACCEPT
            elif action == ShiftReduceParser.OK:
                return output, operations

            # INVALID
            else:
                raise Exception('Invalid')
