from enum import Enum, auto

class TokenType(Enum):
    LBR = auto()            # '('
    RBR = auto()            # ')'
    STAR = auto()           # '*'
    ALT = auto()            # '|'
    LITERAL = auto()        # [a-z]
    LBR_QMARK_COLON = auto()  # '(?:'
    LBR_QMARK_EQUAL = auto()  # '(?='
    LBR_QMARK_NUM = auto()    # '(?[1-9])' 
    EOF = auto()            # End of input

class Token:
    def __init__(self, ttype: TokenType, value=None, pos=None):
        self.type = ttype
        self.value = value
        self.pos = pos

    def __repr__(self):
        return f"Token({self.type}, value={self.value}, pos={self.pos})"

def tokenize(regex: str):
    """Функция токенизации строки регулярного выражения."""
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
                        digit_val = int(next_ch)
                        tokens.append(Token(TokenType.LBR_QMARK_NUM, value=digit_val, pos=i))
                        i += 4  # '(?[n])'
                        continue
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
            tokens.append(Token(TokenType.LITERAL, value=ch, pos=i))
            i += 1
        else:
            raise ValueError(f"Invalid character '{ch}' at position {i}")

    tokens.append(Token(TokenType.EOF, pos=n))
    return tokens
