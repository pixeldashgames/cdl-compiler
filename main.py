from cdl_lexer.lexer import Lexer
from cdl_lexer.table_lexer import regex_table
from cdl_parsing.parser import LR1Parser
import hulk_grammar
from utils.evaluation import evaluate_reverse_parse
from semantic_checking import run_semantic_checker
from hulk_interpreter import InterpreterCollector
import sys


class Hulk:
    def __init__(self, lexer_eof, parser_grammar, verbose = False):
        self.verbose = verbose
        self.lexer = Lexer(regex_table, lexer_eof, verbose)
        self.parser = LR1Parser(parser_grammar, verbose)  

    def build_ast(self, text):
        if self.verbose:
            print("Building AST")
        tokens = self.lexer(text)
        if self.verbose:
            print(tokens)
        right_parse, operations = self.parser([t.token_type for t in tokens])
        ast = evaluate_reverse_parse(right_parse, operations, tokens)
        return ast

    @staticmethod
    def run(code: str, verbose = False):
        hulk = Hulk(hulk_grammar.HG.EOF, hulk_grammar.HG, verbose)
        try:
            ast = hulk.build_ast(code)
        except Exception as e:
            print("Error found at parse-time!")
            print(e.args[0])
            return
            
        errors, context = run_semantic_checker(ast, verbose)
        if errors:
            print("Errors found at compile-time!")
            for e in errors:
                print(e)
            return
        
        interpreter_collector = InterpreterCollector(context)
        interpreter_collector.visit(ast)
        
        try:
            ast.evaluate(context, interpreter_collector.interpreter_context)
        except RuntimeError as e:
            print("Error found at runtime!")
            print(e.args[0])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = 'code.smash'
    with open(path, 'r') as file:
        content = file.read()
    Hulk.run(content)
