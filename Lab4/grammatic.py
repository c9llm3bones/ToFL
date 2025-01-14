from semantic import *
from lexer import *
from ast_ import *

nonterm_idx = 0
TERMS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class GrammarBuilder:
    def __init__(self, capturing_map):
        """
        capturing_map: dict[GroupNode, int], 
           выданный SemanticChecker’ом (GroupNode -> индекс).
        """
        self.capturing_map = capturing_map  # GroupNode -> int
        self.group_counter = 1
        self.group_map = {}   # {GroupNode -> "Gk"}
        self.index2nt = {}    # {int -> "Gk"} чтобы RefNode(num) находил готовый нетерминал
        self.rules = []

    def build_grammar(self, ast):
        # 1) collect_groups: 
        #   регистрируем GroupNode (capture=True) => "Gk".
        #   Заодно сопоставим index2nt[num] = "Gk"
        self.collect_groups(ast)
        # 2) генерируем правила
        self.process_node(ast, "S")
        return self.rules

    def collect_groups(self, node):
        """
        Регистрируем все захватывающие группы:
         - если groupNode.capture == True
         - сопоставляем этому GroupNode свой нетерминал
         - запоминаем, что если capturing_map[node] = N, 
           то index2nt[N] = тот же нетерминал
        """
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
            # Но нужно помнить: index2nt[node.num] должен существовать,
            # если эта группа захватывающая
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
                # Смотрим, какой это нетерминал
                nt_name = self.group_map[node]
                # генерируем правила для содержимого
                self.process_node(node.child, nt_name)
                # текущее правило
                self.rules.append(f"{current_nt} -> {nt_name}")
            else:
                # (?:...) или (?=...) — не захватывающая
                # Встраиваем child в тот же нетерминал
                self.process_node(node.child, current_nt)

        elif isinstance(node, RefNode):
            # Ссылка на группу № node.num
            if node.num not in self.index2nt:
                # нет такой захватывающей группы
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
    """
    Шаг интеграции: 
    1) После парсинга и семантической проверки 
    2) вызываем GrammarBuilder, который строит CFG.
    """
    builder = GrammarBuilder()
    rules = builder.build_grammar(ast)
    return rules
