from lexer import Lexer
from parser import LR1Parser, grammar_init
from utils.evaluation import evaluate_reverse_parse


class Hulk:
    def __init__(self, lexer_table, lexer_eof, parser_grammar):
        self.lexer = Lexer(lexer_table, lexer_eof)
        self.parser = LR1Parser(parser_grammar)

    def build_ast(self, text, verbose=False):
        all_tokens = self.lexer(text)
        tokens = list(filter(lambda token: token.token_type != 'space', all_tokens))
        right_parse, operations = self.parser(tokens)
        ast = evaluate_reverse_parse(right_parse, operations, tokens)
        return ast

    @staticmethod
    def run():
        nonzero_digits = '|'.join(str(n) for n in range(1, 10))
        letters = '|'.join(chr(n) for n in range(ord('a'), ord('z') + 1))

        lexer = [
            ('num', f'({nonzero_digits})(0|{nonzero_digits})*'),
            ('for', 'for'),
            ('foreach', 'foreach'),
            ('space', '  *'),
            ('id', f'({letters})({letters}|0|{nonzero_digits})*')
        ]

        hulk = Hulk(lexer, 'eof', grammar_init())

