import pytest

from pylox import scanner
from pylox.tokens import Token, Tok


@pytest.mark.parametrize(
    "code,expected",
    [
        (
            'print "hello world";',
            [
                Token(
                    Tok.PRINT,
                    "print",
                    None,
                    0,
                    1,
                ),
                Token(
                    Tok.STRING,
                    '"hello world"',
                    "hello world",
                    6,
                    1,
                ),
                Token(Tok.SEMICOLON, ";", None, 19, 1),
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
        (Token(Tok.WHITESPACE, " ", None, 0, 1), False),
        (Token(Tok.COMMENT, "//comment", None, 0, 1), False),
        (Token(Tok.FUN, "fun", None, 0, 1), True),
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
        ("(", 0, 1, Token(Tok.LEFT_PAREN, "(", None, 0, 1)),
        (")", 0, 1, Token(Tok.RIGHT_PAREN, ")", None, 0, 1)),
        ("{", 0, 1, Token(Tok.LEFT_BRACE, "{", None, 0, 1)),
        ("}", 0, 1, Token(Tok.RIGHT_BRACE, "}", None, 0, 1)),
        (",", 0, 1, Token(Tok.COMMA, ",", None, 0, 1)),
        (".", 0, 1, Token(Tok.DOT, ".", None, 0, 1)),
        ("-", 0, 1, Token(Tok.MINUS, "-", None, 0, 1)),
        ("+", 0, 1, Token(Tok.PLUS, "+", None, 0, 1)),
        (";", 0, 1, Token(Tok.SEMICOLON, ";", None, 0, 1)),
        ("*", 0, 1, Token(Tok.STAR, "*", None, 0, 1)),
        ("words.", 5, 1, Token(Tok.DOT, ".", None, 5, 1)),
        ("\n\n.", 2, 3, Token(Tok.DOT, ".", None, 2, 3)),
    ],
)
def test_single_letter_token(code: str, offset: int, line: int, expected: Token):
    result = scanner.single_letter_token(code, offset, line)
    assert result == expected


@pytest.mark.parametrize(
    "code,offset,line,expected",
    [
        (
            ">5",
            0,
            1,
            Token(Tok.GREATER, ">", None, 0, 1),
        ),
        (
            ">=",
            0,
            1,
            Token(Tok.GREATER_EQUAL, ">=", None, 0, 1),
        ),
        (
            "<3",
            0,
            1,
            Token(Tok.LESS, "<", None, 0, 1),
        ),
        (
            "<=",
            0,
            1,
            Token(Tok.LESS_EQUAL, "<=", None, 0, 1),
        ),
        (
            "!2",
            0,
            1,
            Token(Tok.BANG, "!", None, 0, 1),
        ),
        (
            "!=",
            0,
            1,
            Token(Tok.BANG_EQUAL, "!=", None, 0, 1),
        ),
        (
            "!",
            0,
            1,
            Token(Tok.BANG, "!", None, 0, 1),
        ),
    ],
)
def test_dyad_token(code: str, offset: int, line: int, expected: Token):
    result = scanner.dyad_token(code, offset, line)
    assert result == expected


@pytest.mark.parametrize(
    "code,offset,line,expected",
    [
        ("/", 0, 1, Token(Tok.SLASH, "/", None, 0, 1)),
        ("//", 0, 1, Token(Tok.COMMENT, "//", None, 0, 1)),
        ("//hello world", 0, 1, Token(Tok.COMMENT, "//hello world", None, 0, 1)),
        ("//comment\nnot", 0, 1, Token(Tok.COMMENT, "//comment", None, 0, 1)),
        ("code//comment", 4, 1, Token(Tok.COMMENT, "//comment", None, 4, 1)),
    ],
)
def test_slash_comment_token(code: str, offset: int, line: int, expected: Token):
    result = scanner.slash_or_comment_token(code, offset, line)
    assert result == expected


@pytest.mark.parametrize(
    "code,expected",
    [
        ('"hello"', Token(Tok.STRING, '"hello"', "hello", 0, 1)),
        ('"hello\n"', Token(Tok.STRING, '"hello\n"', "hello\n", 0, 1, n_newlines=1)),
    ],
)
def test_string_token(code: str, expected: Token):
    offset = 0
    line = 1
    result = scanner.string_token(code, offset, line)
    assert result == expected


def test_string_token_error():
    code = '"unterminated'
    with pytest.raises(scanner.ScannerError):
        scanner.string_token(code, 0, 1)


@pytest.mark.parametrize(
    "code,expected",
    [
        (
            "52",
            Token(Tok.NUMBER, "52", 52, 0, 1),
        ),
        (
            "3.14",
            Token(Tok.NUMBER, "3.14", 3.14, 0, 1),
        ),
    ],
)
def test_number_token(code: str, expected: Token):
    offset = 0
    line = 1
    result = scanner.number_token(code, offset, line)
    assert result == expected

def test_number_token_is_float():
    code = "42"
    result: Token = scanner.number_token(code, 0, 1)
    assert isinstance(result.value, float)


@pytest.mark.parametrize(
    "code,expected",
    [
        (
            "x=",
            Token(Tok.IDENTIFIER, "x", None, 0, 1),
        ),
        (
            "xy",
            Token(Tok.IDENTIFIER, "xy", None, 0, 1),
        ),
        # KEYWORDS
        (
            "and",
            Token(Tok.AND, "and", None, 0, 1),
        ),
        (
            "class",
            Token(Tok.CLASS, "class", None, 0, 1),
        ),
        (
            "else",
            Token(Tok.ELSE, "else", None, 0, 1),
        ),
        (
            "false",
            Token(Tok.FALSE, "false", None, 0, 1),
        ),
        (
            "for",
            Token(Tok.FOR, "for", None, 0, 1),
        ),
        (
            "fun",
            Token(Tok.FUN, "fun", None, 0, 1),
        ),
        (
            "if",
            Token(Tok.IF, "if", None, 0, 1),
        ),
        (
            "nil",
            Token(Tok.NIL, "nil", None, 0, 1),
        ),
        (
            "or",
            Token(Tok.OR, "or", None, 0, 1),
        ),
        (
            "print",
            Token(Tok.PRINT, "print", None, 0, 1),
        ),
        (
            "return",
            Token(Tok.RETURN, "return", None, 0, 1),
        ),
        (
            "super",
            Token(Tok.SUPER, "super", None, 0, 1),
        ),
        (
            "this",
            Token(Tok.THIS, "this", None, 0, 1),
        ),
        (
            "true",
            Token(Tok.TRUE, "true", None, 0, 1),
        ),
        (
            "var",
            Token(Tok.VAR, "var", None, 0, 1),
        ),
        (
            "while",
            Token(Tok.WHILE, "while", None, 0, 1),
        ),
        # not keyword
        (
            "function",
            Token(Tok.IDENTIFIER, "function", None, 0, 1),
        ),
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
        (" ", Token(Tok.WHITESPACE, " ", None, 0, 1)),
        ("\t", Token(Tok.WHITESPACE, "\t", None, 0, 1)),
        ("\r", Token(Tok.WHITESPACE, "\r", None, 0, 1)),
        # newline should have n_newlines = 1
        ("\n", Token(Tok.WHITESPACE, "\n", None, 0, 1, n_newlines=1)),
        ("   ", Token(Tok.WHITESPACE, "   ", None, 0, 1)),
        ("\n\n\n", Token(Tok.WHITESPACE, "\n\n\n", None, 0, 1, n_newlines=3)),
    ],
)
def test_whitespace_token(code: str, expected: Token):
    offset = 0
    line = 1
    result = scanner.whitespace_token(code, offset, line)
    assert result == expected
