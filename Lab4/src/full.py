from enum import Enum, auto

class TokenType(Enum):
    LBR = auto()            # '('
    RBR = auto()            # ')'
    STAR = auto()            # '*'
    ALT = auto()             # '|'
    LITERAL = auto()         # [a-z]

    LBR_QMARK_COLON = auto()  # '(?:'
    LBR_QMARK_EQUAL = auto()  # '(?='
    LBR_QMARK_NUM = auto()    # '(?[1-9])' 

    EOF = auto()             

class Token:
    def __init__(self, ttype: TokenType, value=None, pos=None):
        self.type = ttype
        self.value = value  
        self.pos = pos    

    def __repr__(self):
        return f"Token({self.type}, value={self.value}, pos={self.pos})"


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
        return (
            f"GroupNode("
            f"capture={self.capture}, "
            f"lookahead={self.lookahead}, "
            f"child={self.child}"
            f")"
        )

class RefNode(RgNode):
    """(?[num])"""
    def __init__(self, num):
        self.num = num
    def __repr__(self):
        return f"RefNode({self.num})"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0 

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, expected_type):
        tk = self.current_token()
        if tk is None:
            raise ValueError("Unexpected end of token stream")
        if tk.type == expected_type:
            self.pos += 1
            return tk
        else:
            raise ValueError(
                f"Expected {expected_type}, got {tk.type} at pos={tk.pos}"
            )

    def lookahead_type(self):
        tk = self.current_token()
        return tk.type if tk else None

    def parseRG(self):
        node = self.parseAlt()
        if self.lookahead_type() != TokenType.EOF:
            tk = self.current_token()
            raise ValueError(
                f"Не все токены были использованы. Остался {tk} в позиции {tk.pos}"
            )
        return node

    def parseAlt(self):
        left = self.parseConcat()
        while self.lookahead_type() == TokenType.ALT:
            self.match(TokenType.ALT)
            right = self.parseConcat()
            left = AltNode(left, right)
        return left

    def parseConcat(self):
        factors = [self.parseFactor()]
        # Пока следующий токен не ) / | / EOF, это конкатенация
        while True:
            ttype = self.lookahead_type()
            if ttype in (TokenType.RBR, TokenType.ALT, TokenType.EOF):
                break
            factors.append(self.parseFactor())

        node = factors[0]
        for f in factors[1:]:
            node = ConcatNode(node, f)
        return node

    def parseFactor(self):
        base_node = self.parseBase()
        if self.lookahead_type() == TokenType.STAR:
            self.match(TokenType.STAR)
            return StarNode(base_node)
        else:
            return base_node

    def parseBase(self):
        """
        parseBase -> 
            LITERAL
            | '(' parseAlt ')'             (захватывающая)
            | '(?:' parseAlt ')'           (не захватывающая)
            | '(?=' parseAlt ')'           (lookahead)
            | '(?[num])'                   (ссылка на выражение)
        """
        tk = self.current_token()

        if tk.type == TokenType.LITERAL:
            # LITERAL
            self.match(TokenType.LITERAL)
            return LiteralNode(tk.value)

        elif tk.type == TokenType.LBR:
            # '(' parseAlt ')'
            self.match(TokenType.LBR)  # съели '('
            child = self.parseAlt()
            self.match(TokenType.RBR)  # съели ')'
            return GroupNode(child, capture=True, lookahead=False)

        elif tk.type == TokenType.LBR_QMARK_COLON:
            # '(?:' parseAlt ')'
            self.match(TokenType.LBR_QMARK_COLON)
            child = self.parseAlt()
            self.match(TokenType.RBR)
            return GroupNode(child, capture=False, lookahead=False)

        elif tk.type == TokenType.LBR_QMARK_EQUAL:
            # '(?=' parseAlt ')'
            self.match(TokenType.LBR_QMARK_EQUAL)
            child = self.parseAlt()
            self.match(TokenType.RBR)
            return GroupNode(child, capture=False, lookahead=True)

        elif tk.type == TokenType.LBR_QMARK_NUM:
            # '(?[num])'
            ref_num = tk.value
            self.match(TokenType.LBR_QMARK_NUM)
            return RefNode(ref_num)

        else:
            raise ValueError(
                f"parseBase: Unexpected token {tk} at pos={tk.pos}"
            )

def tokenize(regex: str):
    tokens = []
    i = 0
    n = len(regex)

    while i < n:
        ch = regex[i]

        if ch == '(':
            if i+1 < n and regex[i+1] == '?':
                if i+2 < n:
                    next_ch = regex[i+2]
                    if next_ch == ':':
                        tokens.append(Token(TokenType.LBR_QMARK_COLON, pos=i))
                        i += 3 
                        continue
                    elif next_ch == '=':
                        tokens.append(Token(TokenType.LBR_QMARK_EQUAL, pos=i))
                        i += 3  
                        continue
                    elif next_ch.isdigit():
                        if next_ch == '0':
                            raise ValueError(
                                f"Неверная ссылка на выражение '(?0' в позиции {i}"
                            )
                        if int(next_ch) < 1 or int(next_ch) > 9:
                            raise ValueError(
                                f"Неверная ссылка '(?{next_ch}' в позиции {i} — должно быть [1-9]"
                            )
                        digit_val = int(next_ch)
                        if i+3 < n and regex[i+3] == ')':
                            tokens.append(Token(TokenType.LBR_QMARK_NUM, 
                                                value=digit_val, 
                                                pos=i))
                            i += 4 
                            continue
                        else:
                            raise ValueError(
                                f"Ожидалась закрывающая скобка после '(?{next_ch}' в позиции {i+3}"
                            )
                    else:
                        raise ValueError(
                            f"Неизвестная конструкция '(?{next_ch}' в позиции {i+2}"
                        )
                else:
                    raise ValueError(f"Незавершённая конструкция '(?' в позиции {i}")
            else:
                tokens.append(Token(TokenType.LBR, pos=i))
                i += 1
        elif ch == ')':
            tokens.append(Token(TokenType.RBR, pos=i))
            i += 1
        elif ch == '*':
            tokens.append(Token(TokenType.STAR, pos=i))
            i += 1
        elif ch == '|':
            tokens.append(Token(TokenType.ALT, pos=i))
            i += 1
        elif ch.isalpha():
            # [a-z]
            tokens.append(Token(TokenType.LITERAL, value=ch, pos=i))
            i += 1
        else:
            raise ValueError(f"Некорректный символ '{ch}' в позиции {i}")

    tokens.append(Token(TokenType.EOF, pos=n))
    return tokens

def parse_regex(regex_str):
    tokens = tokenize(regex_str)
    parser = Parser(tokens)
    ast = parser.parseRG()
    return ast
    
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
                    # захватывающая группа внутри lookahead
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

def print_ast(node, capturing_map, indent=0):
    prefix = "  " * indent  # два пробела на уровень

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

if __name__ == "__main__":
    """examples = [
        "a",
        "(ab)*",       # обычная захватывающая группа + *
        "(?:ab)*|c",   # не захватывающая группа + альтернация
        "(?=xyz)",     # опережающая проверка
        "(?[3])",      # ссылка на выражение
        "ab|c",        # просто альтернация
        "(((xyz)))",   # вложенные скобки
        "(a| (bb)) (a | (?1))",
        "(a(bb))(a(?2))",
        "(a(a|b)*)a(?1)b(?1)",            # должно быть ок
        "(?=a)",        # ок, но внутри опережающей нет групп
        "(?:ab)(xy)", # одна захватывающая группа
        "((ab))",       # две захватывающие
        "((ab))(?2)", # (?[2]) -> ссылка на 2-ю группу, должно быть ок
        "(a (?1))", # Ссылка на 1-ю группу, должно быть ок
        "(a(?1)b|c)",
    ]
    """

    examples = [
        "(a|(?2)b)(a(?1))",
        "(a|(?2))(a|(bb(?1)))(a)",
        "(a|(?2))(a|(bb(?4)))(a)",
        "(a)*((?1))*",
        "(a(?2)b|c)((?1)((?1)))",
        "((a(?1)b|c)|(a|b))((?3)(?2))",
        "(?1)(a|b)",
        "(?1)(a|b)",
        "(a(?1)a|b)",
        "((?1)a|b)",
        "(a|b)*(?1)",
        "(?1)(a|b)*(?1)",
        "(aa|bb)(?1)",
        "(aa|bb)(?1)",
        "(a|(bb))(a|(?2))",
        "(a|(bb))(a|(?3))",
        "(a|(?2))(a|(bb(?1)))",
        "(a(?1)b|c)",
        "(?2)(aa)(bb)",
        "(?3)(aa)(bb)",
    ]
    output_file = "cfg_grammars.txt"

    with open(output_file, "w") as file:
        for ex in examples:
            ex = ex.replace(" ", "")
            print(f"Regex: {ex}")
            checker = SemanticChecker()
            try:
                ast = parse_regex(ex)
                checker.check(ast)

                capturing_map = {}
                for i, grpnode in enumerate(checker.capturing_groups, start=1):
                    capturing_map[grpnode] = i

                builder = GrammarBuilder(capturing_map)
                rules = builder.build_grammar(ast)

                file.write(f"Regex: {ex}\n")
                for r in rules:
                    formatted_rule = r.replace("'", "")  
                    print(formatted_rule)
                    file.write(f"{formatted_rule}\n")
                print()
                file.write("------------------------\n")  

            except ValueError as e:
                print('error: ', e)
            except SemanticError as e:
                print('semantic error: ', e)
            print()