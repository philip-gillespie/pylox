import pytest

from pylox import parser
from pylox import expr
from pylox.tokens import Token, Tok


def test_incomplete_expressions():
    tokens = [
        Token(Tok.STRING, '"cat"', "cat"),
        Token(Tok.GREATER, ">"),
    ]
    expected = expr.Binary(
        left=expr.Literal("cat",1),
        operator=Token(Tok.GREATER, ">"),
        right=expr.Empty(),
        length=2,
    )
    result = parser.next_expression(tokens)
    assert result == expected


def test_equality_expression():
    tokens = [
        Token(Tok.STRING, '"cat"', "cat"),
        Token(Tok.EQUAL_EQUAL, "=="),
        Token(Tok.STRING, '"dog"', "dog"),
    ]
    expected = expr.Binary(
        left=expr.Literal("cat", 1),
        operator=Token(Tok.EQUAL_EQUAL, "=="),
        right=expr.Literal("dog", 1),
        length=3,
    )
    result = parser.equality_expession(tokens)
    assert result == expected


def test_comparison_expression():
    tokens = [
        Token(Tok.NUMBER, "7", 7),
        Token(Tok.GREATER, ">"),
        Token(Tok.NUMBER, "5", 5),
    ]
    expected = expr.Binary(
        left=expr.Literal(7, 1),
        operator=Token(Tok.GREATER, ">"),
        right=expr.Literal(5, 1),
        length=3,
    )
    result = parser.comparison_expression(tokens)
    assert result == expected


def test_term_expression():
    tokens = [
        Token(Tok.NUMBER, "42", 42),
        Token(Tok.PLUS, "+"),
        Token(Tok.NUMBER, "7", 7),
    ]
    expected = expr.Binary(
        left=expr.Literal(42, 1),
        operator=Token(Tok.PLUS, "+"),
        right=expr.Literal(7, 1),
        length=3,
    )
    result = parser.term_expression(tokens)
    assert result == expected


@pytest.mark.parametrize(
    "tokens,expected",
    [
        # Simple case
        (
            [
                Token(Tok.NUMBER, "5", 5),
                Token(Tok.STAR, "*"),
                Token(Tok.NUMBER, "12", 12),
            ],
            expr.Binary(
                left=expr.Literal(5, 1),
                operator=Token(Tok.STAR, "*"),
                right=expr.Literal(12, 1),
                length=3,
            ),
        ),
        # Nested case
        (
            [
                Token(Tok.MINUS, "-"),
                Token(Tok.NUMBER, "3", 3),
                Token(Tok.SLASH, "/"),
                Token(Tok.NUMBER, "4", 4),
            ],
            expr.Binary(
                left=expr.Unary(
                    operator=Token(Tok.MINUS, "-"),
                    right=expr.Literal(value=3, length=1),
                    length=2,
                ),
                operator=Token(Tok.SLASH, "/"),
                right=expr.Literal(value=4, length=1),
                length=4,
            ),
        ),
    ],
)
def test_factor_expression(tokens: list[Token], expected: expr.Binary):
    result = parser.factor_expression(tokens)
    assert result == expected


@pytest.mark.parametrize(
    "tokens,expected",
    [
        (
            [Token(Tok.MINUS, "-", None), Token(Tok.NUMBER, "12", 12)],
            expr.Unary(Token(Tok.MINUS, "-", None), expr.Literal(12, 1), 2),
        )
    ],
)
def test_unary_expression(tokens: list[Token], expected: expr.Unary):
    result = parser.unary_expression(tokens)
    assert result == expected


@pytest.mark.parametrize(
    "tokens,expected",
    [
        ([Token(Tok.NUMBER, "3.14", 3.14)], expr.Literal(3.14, 1)),
        ([Token(Tok.STRING, '"cats"', "cats")], expr.Literal("cats", 1)),
        ([Token(Tok.NIL, "Nil", None)], expr.Literal(None, 1)),
        ([Token(Tok.TRUE, "true", None)], expr.Literal(True, 1)),
        ([Token(Tok.FALSE, "false", None)], expr.Literal(False, 1)),
    ],
)
def test_primary_expression(tokens: list[Token], expected: expr.Literal):
    result = parser.primary_expression(tokens)
    assert result == expected


@pytest.mark.parametrize(
    "tokens,expected",
    [
        # Basic test case
        (
            [
                Token(Tok.LEFT_PAREN, "(", None),
                Token(Tok.NUMBER, "7", 7),
                Token(Tok.RIGHT_PAREN, ")", None),
            ],
            expr.Grouping(expr.Literal(7, 1), 3),
        )
    ],
)
def test_grouping_expression(tokens: list[Token], expected: expr.Grouping):
    result = parser.grouping_expression(tokens)
    assert result == expected
