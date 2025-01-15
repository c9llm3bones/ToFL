from lexer import *

class RgNode:
    """Base class for AST nodes."""

class LiteralNode(RgNode):
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return f"Literal({self.char})"

class AltNode(RgNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Alt({self.left}, {self.right})"

class ConcatNode(RgNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Concat({self.left}, {self.right})"

class StarNode(RgNode):
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Star({self.child})"

class GroupNode(RgNode):
    def __init__(self, child, capture=True, lookahead=False):
        self.child = child
        self.capture = capture
        self.lookahead = lookahead

    def __repr__(self):
        return f"Group(capture={self.capture}, lookahead={self.lookahead}, child={self.child})"

class RefNode(RgNode):
    def __init__(self, num):
        self.num = num

    def __repr__(self):
        return f"RefNode({self.num})"


def print_ast(node, capturing_map, indent=0):
    prefix = "  " * indent 

    if node is None:
        print(prefix + "(empty)")
        return

    if isinstance(node, LiteralNode):
        print(prefix + f"Letter '{node.char}'")

    elif isinstance(node, AltNode):
        print(prefix + "Alt")
        print_ast(node.left, capturing_map, indent+1)
        print_ast(node.right, capturing_map, indent+1)

    elif isinstance(node, ConcatNode):
        print(prefix + "Concat")
        print_ast(node.left, capturing_map, indent+1)
        print_ast(node.right, capturing_map, indent+1)

    elif isinstance(node, StarNode):
        print(prefix + "Star")
        print_ast(node.child, capturing_map, indent+1)

    elif isinstance(node, GroupNode):
        if node.capture and node in capturing_map:
            group_num = capturing_map[node]
            print(prefix + f"Group #{group_num}")
        else:
            if node.lookahead:
                print(prefix + "Group (lookahead)")
            else:
                print(prefix + "Group (non-capt)")
        print_ast(node.child, capturing_map, indent+1)

    elif isinstance(node, RefNode):
        print(prefix + f"QRef -> group {node.num}")

    else:
        print(prefix + f"Unknown node type: {node}")
