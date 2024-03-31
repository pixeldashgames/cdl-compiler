
class Node:
    def evaluate(self):
        raise NotImplementedError()


class AtomicNode(Node):
    def __init__(self, lex):
        self.lex = lex


class UnaryNode(Node):
    def __init__(self, node: Node):
        self.node = node


class BinaryNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right
