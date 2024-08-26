"""
test_parser_functions.py

Unit tests for parsing function definitions and calls.
"""

from pylox import expr, parser
from pylox.tokens import Token, Tok


class TestCallExpression:
    """Unit tests for `call_expression`."""

    def test_no_arguments(self):
        tokens = [
            Token(Tok.IDENTIFIER, "my_fn"),
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.RIGHT_PAREN, ")"),
        ]
        result, offset = parser.call_expression(tokens, 0)
        expected = expr.Call(
            callee=expr.Variable(Token(Tok.IDENTIFIER, "my_fn")),
            paren=Token(Tok.LEFT_PAREN, "("),
            arguments=[],
        )
        assert result == expected
        assert offset == 3

    def test_one_argument(self):
        tokens = [
            Token(Tok.IDENTIFIER, "square"),
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.NUMBER, "5", 5.0),
            Token(Tok.RIGHT_PAREN, ")"),
        ]
        result, offset = parser.call_expression(tokens, 0)
        expected = expr.Call(
            callee=expr.Variable(Token(Tok.IDENTIFIER, "square")),
            paren=Token(Tok.LEFT_PAREN, "("),
            arguments=[expr.Literal(5.0)],
        )
        assert result == expected
        assert offset == 4

    def test_two_arguments(self):
        tokens = [
            Token(Tok.IDENTIFIER, "add"),
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.NUMBER, "5", 5.0),
            Token(Tok.COMMA, ","),
            Token(Tok.NUMBER, "3", 3.0),
            Token(Tok.RIGHT_PAREN, ")"),
        ]
        result, offset = parser.call_expression(tokens, 0)
        expected = expr.Call(
            callee=expr.Variable(Token(Tok.IDENTIFIER, "add")),
            paren=Token(Tok.LEFT_PAREN, "("),
            arguments=[
                expr.Literal(5.0),
                expr.Literal(3.0),
            ],
        )
        assert result == expected
        assert offset == 6
