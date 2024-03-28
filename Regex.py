from utils.tools.automata import NFA, DFA, nfa_to_dfa
from utils.tools.automata import automata_union, automata_concatenation, automata_closure, automata_minimization
from utils.pycompiler import Grammar
from utils.utils import Token
from utils.tools.parsing import metodo_predictivo_no_recursivo
from utils.tools.evaluation import evaluate_parse
from utils.ast import AtomicNode, UnaryNode, BinaryNode

EPSILON = 'ε'

class EpsilonNode(AtomicNode):
    def evaluate(self):
        nfa = NFA(states=2, finals=[1], transitions={
            (0,'ε'):[1]
        })    
        return nfa

EpsilonNode(EPSILON).evaluate()

class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        
        nfa = NFA(states=2, finals=[1], transitions={
            (0, s):[1]
        })
        return nfa

SymbolNode('a').evaluate()

class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value : NFA):
        nfa = automata_closure(value)
        return nfa
    
ClosureNode(SymbolNode('a')).evaluate()

class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        nfa = automata_union(lvalue,rvalue)
        return nfa

UnionNode(SymbolNode('a'), SymbolNode('b')).evaluate()

class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        nfa = automata_concatenation(lvalue,rvalue)

        return nfa

ConcatNode(SymbolNode('a'), SymbolNode('b')).evaluate()

class RangeNode(Node):
    def __init__(self, left_lex, right_lex) -> None:
        self.lvalue = left_lex
        self.rvalue = right_lex
    
    def evaluate(self):
        lascii, rascii = ord(self.lvalue), ord(self.rvalue)
        aggregate = SymbolNode(self.lvalue).evaluate()
        
        for i in range(rascii - lascii + 1):
            aggregate = automata_union(aggregate, SymbolNode(chr(lascii + i)).evaluate())
            
        return aggregate
    
RangeNode(SymbolNode('a'), SymbolNode('z')).evaluate()




G = Grammar()

E = G.NonTerminal('E', True)
T, F, A = G.NonTerminals('T F A')
pipe, star, opar, cpar, symbol, epsilon = G.Terminals('| * ( ) symbol ε')

E %= E + pipe + T, lambda s: UnionNode(s[1], s[3])
E %= T, lambda s: s[1]

T %= T + F, lambda s: ConcatNode(s[1], s[2])
T %= F, lambda s: s[1]

F %= A + star, lambda s: ClosureNode(s[1])
F %= A, lambda s: s[1]

A %= symbol, lambda s: SymbolNode(s[1])
A %= epsilon, lambda s: EpsilonNode(s[1])
A %= opar + E + cpar, lambda s: s[2]

def regex_tokenizer(text, G, skip_whitespaces=True):

    tokens = []

    for char in text:
        if skip_whitespaces and char.isspace():
            continue
        elif char == "|" :
            tokens.append(Token("|", pipe))
        elif char == "*" :
            tokens.append(Token("*", star))
        elif char == "(" :
            tokens.append(Token("(", opar))
        elif char == ")" :
            tokens.append(Token(")", cpar))
        elif char == "ε" :
            tokens.append(Token("ε", epsilon))
        
        else :
            tokens.append(Token(char, symbol))
    
    tokens.append(Token('$', G.EOF))
    return tokens

class Regex:

    def __init__(self, exp):
        self.exp = exp

    def automaton(self):

        tokens = regex_tokenizer(self, G)
        parser = metodo_predictivo_no_recursivo(G)
        left_parse = parser(tokens)
        ast = evaluate_parse(left_parse, tokens)
        nfa = ast.evaluate()
        dfa = nfa_to_dfa(nfa)
        mini = automata_minimization(dfa)

        return mini
    
