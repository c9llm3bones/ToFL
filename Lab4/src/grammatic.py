from semantic import *
from lexer import *
from ast_ import *

nonterm_idx = 0
TERMS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class GrammarBuilder:
    def __init__(self, capturing_map):
        self.capturing_map = capturing_map  
        self.group_counter = 1
        self.group_map = {}   
        self.index2nt = {}    
        self.rules = []

    def build_grammar(self, ast):
        self.collect_groups(ast)
        self.process_node(ast, "S")
        return self.rules

    def collect_groups(self, node):
        if isinstance(node, GroupNode):

            if node.capture:
                idx = self.capturing_map[node]  
                if node not in self.group_map:
                    nt_name = TERMS[self.group_counter]
                    self.group_counter += 1
                    self.group_map[node] = nt_name
                    self.index2nt[idx] = nt_name
            self.collect_groups(node.child)

        elif isinstance(node, AltNode):
            self.collect_groups(node.left)
            self.collect_groups(node.right)
        elif isinstance(node, ConcatNode):
            self.collect_groups(node.left)
            self.collect_groups(node.right)
        elif isinstance(node, StarNode):
            self.collect_groups(node.child)
        elif isinstance(node, RefNode):
            # RefNode сам по себе не создаёт нетерминал,
            pass
        elif isinstance(node, LiteralNode):
            pass

    def process_node(self, node, current_nt):
        if isinstance(node, LiteralNode):
            self.rules.append(f"{current_nt} -> '{node.char}'")

        elif isinstance(node, AltNode):
            left_nt = self.new_nt()
            right_nt = self.new_nt()
            self.process_node(node.left, left_nt)
            self.process_node(node.right, right_nt)
            self.rules.append(f"{current_nt} -> {left_nt} | {right_nt}")

        elif isinstance(node, ConcatNode):
            left_nt = self.new_nt()
            right_nt = self.new_nt()
            self.process_node(node.left, left_nt)
            self.process_node(node.right, right_nt)
            self.rules.append(f"{current_nt} -> {left_nt} {right_nt}")

        elif isinstance(node, StarNode):
            child_nt = self.new_nt()
            self.process_node(node.child, child_nt)
            self.rules.append(f"{current_nt} -> {child_nt} {current_nt} | eps")

        elif isinstance(node, GroupNode):
            if node.capture:
                nt_name = self.group_map[node]
                self.process_node(node.child, nt_name)
                self.rules.append(f"{current_nt} -> {nt_name}")
            else:
                self.process_node(node.child, current_nt)

        elif isinstance(node, RefNode):
            if node.num not in self.index2nt:
                raise ValueError(f"RefNode: нет нетерминала для (?[{node.num}])")
            ref_nt = self.index2nt[node.num]
            self.rules.append(f"{current_nt} -> {ref_nt}")

        else:
            raise ValueError(f"process_node: неизвестный тип узла {node}")

    def new_nt(self):
        nt_name = TERMS[self.group_counter]
        #nt_name = f"G{self.group_counter}"
        self.group_counter += 1
        return nt_name

def generate_cfg(ast):
    builder = GrammarBuilder()
    rules = builder.build_grammar(ast)
    return rules
