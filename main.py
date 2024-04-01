from cdl_lexer.lexer import Lexer
from cdl_lexer.table_lexer import regex_table
from cdl_parsing.parser import LR1Parser
import hulk_grammar
from utils.evaluation import evaluate_reverse_parse


class Hulk:
    def __init__(self, lexer_eof, parser_grammar):
        self.lexer = Lexer(regex_table, lexer_eof)
#        self.parser = LR1Parser(parser_grammar)

    def build_ast(self, text, verbose=False):
        print("Building AST")
        all_tokens = self.lexer(text)
        print(all_tokens)
        tokens = list(filter(lambda token: token.token_type != 'space', all_tokens))
        print(tokens)
        #right_parse, operations = self.parser(tokens)
        #ast = evaluate_reverse_parse(right_parse, operations, tokens)
        #return ast

    @staticmethod
    def run(code: str):
        hulk = Hulk('$', hulk_grammar.HG)
        print(hulk.build_ast(code))


if __name__ == '__main__':
    Hulk.run("print(\"Hello World\");")
