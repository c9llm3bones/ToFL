from ast_ import *
from lexer import *
from parser import *

class SemanticError(Exception):
    pass

def check_init(
    node: RgNode, 
    in_set: set[int], 
    in_progress: set[int], 
    capturing_map: dict[GroupNode, int]
) -> set[int]:
    if node is None:
        return in_set

    # --- Literal ---
    if isinstance(node, LiteralNode):
        return in_set

    # --- RefNode (?[num]) ---
    elif isinstance(node, RefNode):
        #ref_num = node.num
        #if ref_num not in in_set and ref_num not in in_progress:
        #    raise SemanticError(
        #        f"Ссылка (?[{ref_num}]) пытается обратиться к группе, "
        #        f"которая не инициализирована и не в рекурсивном процессе."
        #    )
        return in_set

    # --- GroupNode ---
    elif isinstance(node, GroupNode):
        idx = capturing_map.get(node)  
        if idx is not None:
            #old_in_progress = set(in_progress)
            new_in_progress = set(in_progress)
            new_in_progress.add(idx)

            child_out = check_init(node.child, in_set, new_in_progress, capturing_map)

            out_set = set(child_out)
            out_set.add(idx)

            return out_set
        else:
            # capture=False => (?:...) или (?=...)
            return check_init(node.child, in_set, in_progress, capturing_map)

    # --- AltNode ---
    elif isinstance(node, AltNode):
        left_out = check_init(node.left, in_set, in_progress, capturing_map)
        right_out = check_init(node.right, in_set, in_progress, capturing_map)
        return left_out & right_out

    # --- ConcatNode ---
    elif isinstance(node, ConcatNode):
        left_out = check_init(node.left, in_set, in_progress, capturing_map)
        right_out = check_init(node.right, left_out, in_progress, capturing_map)
        return right_out

    # --- StarNode ---
    elif isinstance(node, StarNode):
        child_out = check_init(node.child, in_set, in_progress, capturing_map)
        return in_set | child_out # in_set & child_out

    else:
        raise SemanticError(f"check_init: неизвестный тип узла {node!r}")

class SemanticChecker:
    def __init__(self):
        self.capturing_groups = [] 
        self.current_path_lookahead_level = 0

    def check(self, ast: RgNode):
 
        self._collect_groups(ast)

        if len(self.capturing_groups) > 9:
            raise SemanticError(
                f"Слишком много захватывающих групп: {len(self.capturing_groups)} (максимум 9)"
            )

        self._check_references(ast)

        capturing_map = {}
        for i, gnode in enumerate(self.capturing_groups, start=1):
            capturing_map[gnode] = i

        check_init(ast, set(), set(), capturing_map)
        print_ast(ast, capturing_map)
        return True

    def _collect_groups(self, node: RgNode):

        if node is None:
            return

        if isinstance(node, LiteralNode):
            return

        elif isinstance(node, AltNode):
            self._collect_groups(node.left)
            self._collect_groups(node.right)

        elif isinstance(node, ConcatNode):
            self._collect_groups(node.left)
            self._collect_groups(node.right)

        elif isinstance(node, StarNode):
            self._collect_groups(node.child)

        elif isinstance(node, GroupNode):
            if node.lookahead:
                if self.current_path_lookahead_level >= 1:
                    raise SemanticError("Вложенный lookahead (?=...) запрещён")
                self.current_path_lookahead_level += 1
                self._collect_groups(node.child)
                self.current_path_lookahead_level -= 1
            else:
                # обычная или (?:...) группа
                if self.current_path_lookahead_level > 0 and node.capture:
                    raise SemanticError(
                        "Захватывающая группа внутри опережающего блока (?=...) запрещена"
                    )
                if node.capture:
                    self.capturing_groups.append(node)
                self._collect_groups(node.child)

        elif isinstance(node, RefNode):
            # (?[num]) внутри lookahead 
            # if self.current_path_lookahead_level > 0:
            #     raise SemanticError("Ссылка (?[num]) внутри (?=...) запрещена.")
            return

        else:
            raise SemanticError(f"_collect_groups: неизвестный тип узла {node!r}")

    def _check_references(self, node: RgNode):
        if node is None:
            return

        if isinstance(node, LiteralNode):
            return

        elif isinstance(node, AltNode):
            self._check_references(node.left)
            self._check_references(node.right)

        elif isinstance(node, ConcatNode):
            self._check_references(node.left)
            self._check_references(node.right)

        elif isinstance(node, StarNode):
            self._check_references(node.child)

        elif isinstance(node, GroupNode):
            self._check_references(node.child)

        elif isinstance(node, RefNode):
            if node.num > len(self.capturing_groups):
                raise SemanticError(
                    f"Ссылка (?[{node.num}]) указывает на несуществующую группу "
                    f"(всего захватывающих групп: {len(self.capturing_groups)})"
                )

        else:
            raise SemanticError(f"_check_references: неизвестный тип узла {node!r}")
