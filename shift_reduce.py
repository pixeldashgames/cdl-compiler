from utils.pycompiler import (Grammar, SintacticException)
from typing import List
from utils.utils import Token


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

    def __call__(self, w: List[Token]):
        stack = [0]
        cursor = 0
        output = []
        actions = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, '<---||--->', w[cursor:])

            try:
                action, tag = self.action[state, lookahead]
            except Exception as e:
                # Follow the row state and give the terminals that have either shift or reduce
                # actions
                actions = {k[1] for k in self.action if k[0] == state}
                raise Exception(
                    f"Unexpected token {lookahead} on cursor {cursor}, expected one of {actions}")
            if action == ShiftReduceParser.SHIFT:
                stack.append(lookahead)
                stack.append(tag)
                cursor += 1
            elif action == ShiftReduceParser.REDUCE:
                production = tag
                left, right = production
                for _ in range(2 * len(right)):
                    stack.pop()
                state = stack[-1]
                stack.append(left)
                stack.append(self.goto[state, left])
                output.append(production)
            elif action == ShiftReduceParser.OK:
                break

            actions.append(action)

        return output, actions
