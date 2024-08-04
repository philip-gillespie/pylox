from typing import Iterator
from pylox.tokens import Token, Tok


def scan(code: str) -> list[Token]:
    """Scans the code string returning a list of corresponding Tokens"""
    tokens = generate_tokens(code)
    useful_tokens = filter(is_useful_token, tokens)
    return list(useful_tokens)


class ScannerError(Exception):
    def __init__(self, line, message):
        self.line = line
        self.message = message


def generate_tokens(code: str) -> Iterator[Token]:
    i: int = 0
    line: int = 1
    while i < len(code):
        token: Token = get_next_token(code, i, line)
        i = i + token.length
        line = line + token.n_newlines
        yield (token)
    return None


USELESS_TOKENS = [Tok.WHITESPACE, Tok.COMMENT]


def is_useful_token(t: Token) -> bool:
    """
    Return False if the token is for whitespace or comment.
    Otherwise return True.
    """
    if t.token_type in USELESS_TOKENS:
        return False
    return True


def get_next_token(code: str, offset: int, line: int) -> Token:
    char = code[offset]
    if char in single_letter_tokens:
        return single_letter_token(code, offset, line)
    if char in dyad_tokens:
        return dyad_token(code, offset, line)
    if char == "/":
        return slash_or_comment_token(code, offset, line)
    if char == '"':
        return string_token(code, offset, line)
    if char.isdigit():
        return number_token(code, offset, line)
    if char.isidentifier():  # a-z,a-z,_
        return keyword_or_identifier_token(code, offset, line)
    if char.isspace():
        return whitespace_token(code, offset, line)
    raise ScannerError(line, f"Unexpected Character: {char}")


def get(code: str, offset: int) -> str:
    """
    If possible, return the character at index `offset`.
    If if impossible due to the length of the code, return "".
    """
    try:
        return code[offset]
    except IndexError:
        return ""


single_letter_tokens = {
    "(": Tok.LEFT_PAREN,
    ")": Tok.RIGHT_PAREN,
    "{": Tok.LEFT_BRACE,
    "}": Tok.RIGHT_BRACE,
    ",": Tok.COMMA,
    ".": Tok.DOT,
    "-": Tok.MINUS,
    "+": Tok.PLUS,
    ";": Tok.SEMICOLON,
    "*": Tok.STAR,
}


def single_letter_token(code: str, offset: int, line: int) -> Token:
    """Return a token, given that it is in `single letter tokens`."""
    char: str = code[offset]
    token_type: Tok = single_letter_tokens[char]
    return Token(token_type, char, offset, line)


dyad_tokens = {
    "!": {"=": Tok.BANG_EQUAL, "<default>": Tok.BANG},
    "=": {"=": Tok.EQUAL_EQUAL, "<default>": Tok.EQUAL},
    "<": {"=": Tok.LESS_EQUAL, "<default>": Tok.LESS},
    ">": {"=": Tok.GREATER_EQUAL, "<default>": Tok.GREATER},
}


def dyad_token(code: str, offset: int, line: int) -> Token:
    char: str = code[offset]
    options: dict[str, Tok] = dyad_tokens[char]
    next_char: str = get(code, offset + 1)
    if next_char in options:
        token_type: Tok = options[next_char]
        return Token(token_type, char + next_char, offset, line, length=2)
    token_type: Tok = options["<default>"]
    return Token(token_type, char, offset, line)


def slash_or_comment_token(code: str, offset: int, line: int) -> Token:
    next_character: str = get(code, offset + 1)
    if next_character != "/":  # not a comment
        return Token(Tok.SLASH, "/", offset, line)
    # THIS IS A COMMENT TOKEN
    next_newline: int = code.find("\n", offset)
    if next_newline == -1:  # not found in string
        length = len(code) - offset
        text = code[offset:]
    else:
        length = next_newline - offset
        text = code[offset:next_newline]
    return Token(Tok.COMMENT, text, offset, line, length=length)


def string_token(code: str, offset: int, line: int) -> Token:
    i = offset + 1
    n_newlines = 0
    char = get(code, i)
    while char != '"':
        i += 1
        char = get(code, i)
        if char == "\n":
            n_newlines += 1
        if char == "":  # End of file
            raise ScannerError(
                line,
                f"Error: Unterminated string",
            )
    value = code[offset + 1 : i]
    length = len(value) + 2
    return Token(
        Tok.STRING,
        value,
        offset,
        line,
        length=length,
        n_newlines=n_newlines,
    )


def number_token(code: str, offset: int, line: int) -> Token:
    """
    Return a Token for a numeric type.
    Given that `code` at offset is numeric.
    """
    i = offset + 1
    char: str = get(code, i)
    while char.isdigit():
        i += 1
        char = get(code, i)
    # check for decimal point then digit eg `.2`
    next_char = get(code, i + 1)
    if (char == ".") and (next_char.isdigit()):
        i += 2
        char = get(code, i)
        while char.isdigit():
            i += 1
            char = get(code, i)
    # `i` will always be index following the last digit
    return Token(
        token_type=Tok.NUMBER,
        lexeme=code[offset:i],
        start=offset,
        line=line,
        length=i - offset,
    )


KEYWORDS = {
    "and": Tok.AND,
    "class": Tok.CLASS,
    "else": Tok.ELSE,
    "false": Tok.FALSE,
    "for": Tok.FOR,
    "fun": Tok.FUN,
    "if": Tok.IF,
    "nil": Tok.NIL,
    "or": Tok.OR,
    "print": Tok.PRINT,
    "return": Tok.RETURN,
    "super": Tok.SUPER,
    "this": Tok.THIS,
    "true": Tok.TRUE,
    "var": Tok.VAR,
    "while": Tok.WHILE,
}


def keyword_or_identifier_token(code: str, offset: int, line: int) -> Token:
    i: int = offset + 1
    char: str = get(code, i)
    while char.isidentifier() or char.isalnum():
        i += 1
        char = get(code, i)
    lexeme: str = code[offset:i]
    if lexeme in KEYWORDS:
        token_type = KEYWORDS[lexeme]
        return Token(token_type, lexeme, offset, line, length=i - offset)
    return Token(Tok.IDENTIFIER, lexeme, offset, line, length=i - offset)


def whitespace_token(code: str, offset: int, line: int) -> Token:
    i: int = offset
    char: str = get(code, i)
    n_newlines = 0
    while char.isspace():
        if char == "\n":
            n_newlines += 1
        i += 1
        char = get(code, i)
    lexeme: str = code[offset:i]
    return Token(
        Tok.WHITESPACE,
        lexeme,
        offset,
        line,
        length=i - offset,
        n_newlines=n_newlines,
    )
