from lexer import *
from ast_ import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0 

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, expected_type):
        """Съедает токен ожидаемого типа и возвращает его.
            Если тип не совпадает, бросает ошибку."""
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
        """
        parseAlt -> parseConcat ( '|' parseConcat )*
        """
        left = self.parseConcat()
        while self.lookahead_type() == TokenType.ALT:
            self.match(TokenType.ALT)
            right = self.parseConcat()
            left = AltNode(left, right)
        return left

    def parseConcat(self):
        """
        parseConcat -> parseFactor+
        Т.е. хотя бы один factor, а затем могут идти ещё factor-ы
        """
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
        """
        parseFactor -> parseBase ('*')?
        """
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

def parse_regex(regex_str):
    tokens = tokenize(regex_str)
    parser = Parser(tokens)
    ast = parser.parseRG()
    return ast