import pytest

from pylox import scanner
from pylox.tokens import Token, Tok


@pytest.mark.parametrize(
    "code,expected",
    [
        (
            'print "hello world";',
            [
                Token(Tok.PRINT, "print", 0, 1, length=5),
                Token(Tok.STRING, "hello world", 6, 1, length=13),
                Token(Tok.SEMICOLON, ";", 19, 1),
            ],
        )
    ],
)
def test_scan(code: str, expected: list[Token]):
    result = scanner.scan(code)
    assert result == expected


@pytest.mark.parametrize(
    "token,expected",
    [
        (Token(Tok.WHITESPACE, " ", 0, 1), False),
        (Token(Tok.COMMENT, "//comment", 0, 1), False),
        (Token(Tok.FUN, "fun", 0, 1), True),
    ],
)
def test_is_useful_token(token: Token, expected: bool):
    result = scanner.is_useful_token(token)
    assert result == expected


@pytest.mark.parametrize(
    "code,expected",
    [
        ("+", Tok.PLUS),
        (">", Tok.GREATER),
        ("!=", Tok.BANG_EQUAL),
        ("/", Tok.SLASH),
        ("//", Tok.COMMENT),
        ('"hello"', Tok.STRING),
        ("3.14", Tok.NUMBER),
        ("var", Tok.VAR),
        ("cats", Tok.IDENTIFIER),
        (" \n\t", Tok.WHITESPACE),
    ],
)
def test_get_next_token(code: str, expected: Tok):
    """Test this function correctly deligates."""
    offset = 0
    line = 1
    token = scanner.get_next_token(code, offset, line)
    result = token.token_type
    assert result == expected


@pytest.mark.parametrize(
    "code,offset,expected",
    [
        ("abc", 0, "a"),
        ("abc", 2, "c"),
        ("abc", 5, ""),
    ],
)
def test_get(code: str, offset: int, expected: str):
    result = scanner.get(code, offset)
    assert result == expected


@pytest.mark.parametrize(
    "code,offset,line,expected",
    [
        ("(", 0, 1, Token(Tok.LEFT_PAREN, "(", 0, 1)),
        (")", 0, 1, Token(Tok.RIGHT_PAREN, ")", 0, 1)),
        ("{", 0, 1, Token(Tok.LEFT_BRACE, "{", 0, 1)),
        ("}", 0, 1, Token(Tok.RIGHT_BRACE, "}", 0, 1)),
        (",", 0, 1, Token(Tok.COMMA, ",", 0, 1)),
        (".", 0, 1, Token(Tok.DOT, ".", 0, 1)),
        ("-", 0, 1, Token(Tok.MINUS, "-", 0, 1)),
        ("+", 0, 1, Token(Tok.PLUS, "+", 0, 1)),
        (";", 0, 1, Token(Tok.SEMICOLON, ";", 0, 1)),
        ("*", 0, 1, Token(Tok.STAR, "*", 0, 1)),
        ("words.", 5, 1, Token(Tok.DOT, ".", 5, 1)),
        ("\n\n.", 2, 3, Token(Tok.DOT, ".", 2, 3)),
    ],
)
def test_single_letter_token(code: str, offset: int, line: int, expected: Token):
    result = scanner.single_letter_token(code, offset, line)
    assert result == expected


@pytest.mark.parametrize(
    "code,offset,line,expected",
    [
        (">5", 0, 1, Token(Tok.GREATER, ">", 0, 1, length=1)),
        (">=", 0, 1, Token(Tok.GREATER_EQUAL, ">=", 0, 1, length=2)),
        ("<3", 0, 1, Token(Tok.LESS, "<", 0, 1, length=1)),
        ("<=", 0, 1, Token(Tok.LESS_EQUAL, "<=", 0, 1, length=2)),
        ("!2", 0, 1, Token(Tok.BANG, "!", 0, 1, length=1)),
        ("!=", 0, 1, Token(Tok.BANG_EQUAL, "!=", 0, 1, length=2)),
        ("!", 0, 1, Token(Tok.BANG, "!", 0, 1, length=1)),
    ],
)
def test_dyad_token(code: str, offset: int, line: int, expected: Token):
    result = scanner.dyad_token(code, offset, line)
    assert result == expected


@pytest.mark.parametrize(
    "code,offset,line,expected",
    [
        ("/", 0, 1, Token(Tok.SLASH, "/", 0, 1)),
        ("//", 0, 1, Token(Tok.COMMENT, "//", 0, 1, length=2)),
        ("//hello world", 0, 1, Token(Tok.COMMENT, "//hello world", 0, 1, length=13)),
        ("//comment\nnot", 0, 1, Token(Tok.COMMENT, "//comment", 0, 1, length=9)),
        ("code//comment", 4, 1, Token(Tok.COMMENT, "//comment", 4, 1, length=9)),
    ],
)
def test_slash_comment_token(code: str, offset: int, line: int, expected: Token):
    result = scanner.slash_or_comment_token(code, offset, line)
    assert result == expected


@pytest.mark.parametrize(
    "code,offset,line,expected",
    [
        ('"hello"', 0, 1, Token(Tok.STRING, "hello", 0, 1, length=7)),
        ('"hello\n"', 0, 1, Token(Tok.STRING, "hello\n", 0, 1, length=8, n_newlines=1)),
    ],
)
def test_string_token(code: str, offset: int, line: int, expected: Token):
    result = scanner.string_token(code, offset, line)
    assert result == expected


def test_string_token_error():
    code = '"unterminated'
    with pytest.raises(scanner.ScannerError):
        scanner.string_token(code, 0, 1)


@pytest.mark.parametrize(
    "code,expected",
    [
        ("52", Token(Tok.NUMBER, "52", 0, 1, length=2)),
        ("3.14", Token(Tok.NUMBER, "3.14", 0, 1, length=4)),
    ],
)
def test_number_token(code: str, expected: Token):
    offset = 0
    line = 1
    result = scanner.number_token(code, offset, line)
    assert result == expected


@pytest.mark.parametrize(
    "code,expected",
    [
        ("x=", Token(Tok.IDENTIFIER, "x", 0, 1, length=1)),
        ("xy", Token(Tok.IDENTIFIER, "xy", 0, 1, length=2)),
        # KEYWORDS
        ("and", Token(Tok.AND, "and", 0, 1, length=3)),
        ("class", Token(Tok.CLASS, "class", 0, 1, length=5)),
        ("class", Token(Tok.CLASS, "class", 0, 1, length=5)),
        ("else", Token(Tok.ELSE, "else", 0, 1, length=4)),
        ("false", Token(Tok.FALSE, "false", 0, 1, length=5)),
        ("for", Token(Tok.FOR, "for", 0, 1, length=3)),
        ("fun", Token(Tok.FUN, "fun", 0, 1, length=3)),
        ("if", Token(Tok.IF, "if", 0, 1, length=2)),
        ("nil", Token(Tok.NIL, "nil", 0, 1, length=3)),
        ("or", Token(Tok.OR, "or", 0, 1, length=2)),
        ("print", Token(Tok.PRINT, "print", 0, 1, length=5)),
        ("return", Token(Tok.RETURN, "return", 0, 1, length=6)),
        ("super", Token(Tok.SUPER, "super", 0, 1, length=5)),
        ("this", Token(Tok.THIS, "this", 0, 1, length=4)),
        ("true", Token(Tok.TRUE, "true", 0, 1, length=4)),
        ("var", Token(Tok.VAR, "var", 0, 1, length=3)),
        ("while", Token(Tok.WHILE, "while", 0, 1, length=5)),
        # not keyword
        ("function", Token(Tok.IDENTIFIER, "function", 0, 1, length=8)),
    ],
)
def test_keyword_or_identifier_token(code: str, expected: Token):
    offset = 0
    line = 1
    result = scanner.keyword_or_identifier_token(code, offset, line)
    assert result == expected


@pytest.mark.parametrize(
    "code,expected",
    [
        (" ", Token(Tok.WHITESPACE, " ", 0, 1)),
        ("\t", Token(Tok.WHITESPACE, "\t", 0, 1)),
        ("\r", Token(Tok.WHITESPACE, "\r", 0, 1)),
        # newline should have n_newlines = 1
        ("\n", Token(Tok.WHITESPACE, "\n", 0, 1, n_newlines=1)),
        ("   ", Token(Tok.WHITESPACE, "   ", 0, 1, length=3, n_newlines=0)),
        ("\n\n\n", Token(Tok.WHITESPACE, "\n\n\n", 0, 1, length=3, n_newlines=3)),
    ],
)
def test_whitespace_token(code: str, expected: Token):
    offset = 0
    line = 1
    result = scanner.whitespace_token(code, offset, line)
    assert result == expected
