from cdl_lexer.lexer import Lexer
from cdl_lexer.table_lexer import regex_table
from cdl_parsing.parser import LR1Parser
import hulk_grammar
from utils.evaluation import evaluate_reverse_parse
from semantic_checking import run_semantic_checker
from hulk_interpreter import InterpreterCollector
import sys


class Hulk:
    def __init__(self, lexer_eof, parser_grammar):
        self.lexer = Lexer(regex_table, lexer_eof)
        self.parser = LR1Parser(parser_grammar, True)  # Running this it raises a conflict error

    def build_ast(self, text, verbose=False):
        print("Building AST")
        tokens = self.lexer(text)
        print(tokens)
        # --------------------------------------------------------------------------------------
        # Parser start here --------------------------------------------------------------------
        # --------------------------------------------------------------------------------------
        right_parse, operations = self.parser([t.token_type for t in tokens])
        ast = evaluate_reverse_parse(right_parse, operations, tokens)
        return ast

    @staticmethod
    def run(code: str):
        hulk = Hulk(hulk_grammar.HG.EOF, hulk_grammar.HG)
        ast = hulk.build_ast(code)
        context = run_semantic_checker(ast)
        if context:
            print("Semantic check passed")
        else:
            print("Semantic check failed")
            return
        interpreter_collector = InterpreterCollector(context)
        interpreter_collector.visit(ast)
        ast.evaluate(context, interpreter_collector.interpreter_context)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = 'code.smash'
    with open(path, 'r') as file:
        content = file.read()
    Hulk.run(content)
