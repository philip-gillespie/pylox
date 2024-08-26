import pytest

from pylox import parser, scanner, expr, stmt
from pylox.tokens import Token, Tok


class TestForStatement:
    """Unit tests for `for_statement`."""

    def test_empty_case(self):
        tokens = [
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.SEMICOLON, ";"),
            Token(Tok.SEMICOLON, ";"),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.PRINT, "print"),
            Token(Tok.STRING, '"hello"', "hello"),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.for_statement(tokens, 0)
        expected = stmt.PrintStmt(expr.Literal("hello"))
        assert result == expected
        assert offset == 7

    def test_init_case(self):
        tokens = [
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.VAR, "var"),
            Token(Tok.IDENTIFIER, "x"),
            Token(Tok.EQUAL, "="),
            Token(Tok.NUMBER, "0", 0.0),
            Token(Tok.SEMICOLON, ";"),
            Token(Tok.SEMICOLON, ";"),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.PRINT, "print"),
            Token(Tok.STRING, '"hello"', "hello"),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.for_statement(tokens, 0)
        expected = stmt.Block(
            [
                stmt.Var(
                    name=Token(Tok.IDENTIFIER, "x"),
                    initialiser=expr.Literal(0.0),
                ),
                stmt.PrintStmt(expr.Literal("hello")),
            ]
        )
        assert result == expected
        assert offset == 11

    def test_condition_case(self):
        tokens = [
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.SEMICOLON, ";"),
            Token(Tok.IDENTIFIER, "x"),
            Token(Tok.LESS, "<"),
            Token(Tok.NUMBER, "5", 5.0),
            Token(Tok.SEMICOLON, ";"),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.PRINT, "print"),
            Token(Tok.STRING, '"hello"', "hello"),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.for_statement(tokens, 0)
        expected = stmt.While(
            condition=expr.Binary(
                left=expr.Variable(Token(Tok.IDENTIFIER, "x")),
                operator=Token(Tok.LESS, "<"),
                right=expr.Literal(5.0),
            ),
            body=stmt.PrintStmt(expr.Literal("hello")),
        )
        assert result == expected

    def test_increment_case(self):
        tokens = scanner.scan('(;;x=x+1) print "cats";')
        result, offset = parser.for_statement(tokens, 0)
        expected = stmt.Block(
            [
                stmt.PrintStmt(expr.Literal("cats")),
                stmt.Expression(
                    expr.Assign(
                        name=Token(Tok.IDENTIFIER, "x", None, start=3),
                        value=expr.Binary(
                            left=expr.Variable(
                                Token(Tok.IDENTIFIER, "x", None, start=5)
                            ),
                            operator=Token(Tok.PLUS, "+", start=6),
                            right=expr.Literal(1),
                        ),
                    )
                ),
            ]
        )
        assert result == expected

    def test_full_case(self):
        tokens = [
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.VAR, "var"),
            Token(Tok.IDENTIFIER, "i"),
            Token(Tok.EQUAL, "="),
            Token(Tok.NUMBER, "1", 1.0),
            Token(Tok.SEMICOLON, ";"),
            Token(Tok.IDENTIFIER, "i"),
            Token(Tok.LESS, "<"),
            Token(Tok.NUMBER, "5", 5.0),
            Token(Tok.SEMICOLON, ";"),
            Token(Tok.IDENTIFIER, "i"),
            Token(Tok.EQUAL, "="),
            Token(Tok.IDENTIFIER, "i"),
            Token(Tok.PLUS, "+"),
            Token(Tok.NUMBER, "1", 1.0),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.PRINT, "print"),
            Token(Tok.IDENTIFIER, "i"),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.for_statement(tokens, 0)
        expected = stmt.Block(
            [
                stmt.Var(
                    name=Token(Tok.IDENTIFIER, "i"),
                    initialiser=expr.Literal(1.0),
                ),
                stmt.While(
                    condition=expr.Binary(
                        left=expr.Variable(name=Token(Tok.IDENTIFIER, "i")),
                        operator=Token(Tok.LESS, "<"),
                        right=expr.Literal(5.0),
                    ),
                    body=stmt.Block(
                        [
                            stmt.PrintStmt(
                                expr.Variable(name=Token(Tok.IDENTIFIER, "i"))
                            ),
                            stmt.Expression(
                                expr.Assign(
                                    name=Token(Tok.IDENTIFIER, "i"),
                                    value=expr.Binary(
                                        left=expr.Variable(
                                            name=Token(Tok.IDENTIFIER, "i"),
                                        ),
                                        operator=Token(Tok.PLUS, "+"),
                                        right=expr.Literal(1.0),
                                    ),
                                )
                            ),
                        ]
                    ),
                ),
            ]
        )
        assert result == expected


class TestForStatementInitialiser:
    """Unit tests for `for_statement_initialiser`"""

    def test_no_initialiser(self):
        """Returns None when there is no initialiser."""
        tokens = [Token(Tok.SEMICOLON, ";")]
        result, offset = parser.for_statement_initialiser(tokens, 0)
        assert result is None
        assert offset == 1

    def test_var_initialiser(self):
        """Returns variable declaration if `var` used."""
        tokens = [
            Token(Tok.VAR, "var"),
            Token(Tok.IDENTIFIER, "x"),
            Token(Tok.EQUAL, "="),
            Token(Tok.NUMBER, "0", 0.0),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.for_statement_initialiser(tokens, 0)
        expected = stmt.Var(
            name=Token(Tok.IDENTIFIER, "x"),
            initialiser=expr.Literal(0.0),
        )
        assert result == expected
        assert offset == 5

    def test_expr_initialiser(self):
        """Returns an expression statement if necessary."""
        tokens = [
            Token(Tok.NUMBER, "3", 3.0),
            Token(Tok.MINUS, "-"),
            Token(Tok.NUMBER, "1", 1.0),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.for_statement_initialiser(tokens, 0)
        expected = stmt.Expression(
            expr.Binary(
                left=expr.Literal(3.0),
                operator=Token(Tok.MINUS, "-"),
                right=expr.Literal(1.0),
            )
        )
        assert result == expected
        assert offset == 4
