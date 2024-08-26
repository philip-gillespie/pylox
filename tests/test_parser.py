import pytest

from pylox import parser, scanner, expr, stmt
from pylox.tokens import Token, Tok


class TestParse:
    """Unit tests for parse"""

    def test_var_declaration(self):
        tokens = [
            Token(Tok.VAR, "var"),
            Token(Tok.IDENTIFIER, "x", "x"),
            Token(Tok.EQUAL, "="),
            Token(Tok.NUMBER, "5", 5),
            Token(Tok.SEMICOLON, ";"),
        ]
        result = parser.parse(tokens)
        assert result == [
            stmt.Var(
                Token(Tok.IDENTIFIER, "x", "x"),
                expr.Literal(5),
            )
        ]


class TestGetNextStatement:
    """Unit tests for `get_next_statement`."""

    def test_while_statement(self):
        tokens = [
            Token(Tok.WHILE, "while"),
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.FALSE, "false"),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.PRINT, "print"),
            Token(Tok.STRING, '"hello world"', "hello world"),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.get_statement(tokens, 0)
        expected = stmt.While(
            condition=expr.Literal(False),
            body=stmt.PrintStmt(expr.Literal("hello world")),
        )
        assert result == expected
        assert offset == 7


class TestIfStatement:
    """Unit tests for `if_statement`."""

    def test_single_clause(self):
        tokens = [
            Token(Tok.IF, "if"),
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.TRUE, "true"),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.PRINT, "print"),
            Token(Tok.FALSE, "false"),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.if_statement(tokens, 1)
        expected = stmt.IfStmt(
            condition=expr.Literal(True),
            then_branch=stmt.PrintStmt(
                expr.Literal(False),
            ),
            else_branch=None,
        )
        assert result == expected
        assert offset == 7

    def test_else_branch(self):
        tokens = [
            Token(Tok.IF, "if"),
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.TRUE, "true"),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.PRINT, "print"),
            Token(Tok.FALSE, "false"),
            Token(Tok.SEMICOLON, ";"),
            Token(Tok.ELSE, "else"),
            Token(Tok.PRINT, "print"),
            Token(Tok.TRUE, "true"),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.if_statement(tokens, 1)
        expected = stmt.IfStmt(
            condition=expr.Literal(True),
            then_branch=stmt.PrintStmt(
                expr.Literal(False),
            ),
            else_branch=stmt.PrintStmt(
                expr.Literal(True),
            ),
        )
        assert result == expected
        assert offset == 11

    def test_multiple_else(self):
        """else should attach to the inner most if."""
        tokens = [
            Token(Tok.IF, "if"),
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.TRUE, "true"),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.IF, "if"),
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.FALSE, "false"),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.PRINT, "print"),
            Token(Tok.STRING, '"cats"', "cats"),
            Token(Tok.SEMICOLON, ";"),
            Token(Tok.ELSE, "else"),
            Token(Tok.PRINT, "print"),
            Token(Tok.STRING, '"dogs"', "dogs"),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.if_statement(tokens, 1)
        expected = stmt.IfStmt(
            condition=expr.Literal(True),
            then_branch=stmt.IfStmt(
                condition=expr.Literal(False),
                then_branch=stmt.PrintStmt(expr.Literal("cats")),
                else_branch=stmt.PrintStmt(expr.Literal("dogs")),
            ),
            else_branch=None,
        )
        assert result == expected
        assert offset == 15


class TestWhileStatement:
    """Unit tests for `while_statement`."""

    def test_simple_while(self):
        """Returns a `stmt.While` from correct sequence of tokens."""
        tokens = [
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.TRUE, "true"),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.PRINT, "print"),
            Token(Tok.NUMBER, "3", 3.0),
            Token(Tok.SEMICOLON, ";"),
        ]
        result, offset = parser.while_statement(tokens, 0)
        expected = stmt.While(
            condition=expr.Literal(True),
            body=stmt.PrintStmt(
                expr.Literal(3.0),
            ),
        )
        assert result == expected
        assert offset == 6

    def test_missing_left_paren(self):
        """Raises ParserError when left parenthesis is missing."""
        tokens = [
            Token(Tok.TRUE, "true"),
            Token(Tok.RIGHT_PAREN, ")"),
            Token(Tok.PRINT, "print"),
            Token(Tok.NUMBER, "3", 3.0),
            Token(Tok.SEMICOLON, ";"),
        ]
        with pytest.raises(parser.ParserError):
            parser.while_statement(tokens, 0)

    def test_missing_right_paren(self):
        """Raises ParserError when right parenthesis is missing."""
        tokens = [
            Token(Tok.LEFT_PAREN, "("),
            Token(Tok.TRUE, "true"),
            Token(Tok.PRINT, "print"),
            Token(Tok.NUMBER, "3", 3.0),
            Token(Tok.SEMICOLON, ";"),
        ]
        with pytest.raises(parser.ParserError):
            parser.while_statement(tokens, 0)


class TestGetExpression:
    """Unit tests for `get_expression`."""

    def test_or_expression(self):
        """Returns `Logical` or expression where appropriate."""
        tokens = [
            Token(Tok.TRUE, "true"),
            Token(Tok.OR, "or"),
            Token(Tok.FALSE, "false"),
        ]
        result, offset = parser.get_expression(tokens, 0)
        expected = expr.Logical(
            left=expr.Literal(True),
            operator=Token(Tok.OR, "or"),
            right=expr.Literal(False),
        )
        assert result == expected
        assert offset == 3

    def test_and_expression(self):
        """Returns `Logical` and expression when appropriate."""
        tokens = [
            Token(Tok.TRUE, "true"),
            Token(Tok.AND, "and"),
            Token(Tok.FALSE, "false"),
        ]
        result, offset = parser.get_expression(tokens, 0)
        expected = expr.Logical(
            left=expr.Literal(True),
            operator=Token(Tok.AND, "and"),
            right=expr.Literal(False),
        )
        assert result == expected
        assert offset == 3


class TestAndExpression:
    """Unit tests for `and_expression`."""

    def test_simple_and(self):
        tokens = [
            Token(Tok.TRUE, "true"),
            Token(Tok.AND, "and"),
            Token(Tok.FALSE, "false"),
        ]
        result, offset = parser.and_expression(tokens, 0)
        expected = expr.Logical(
            left=expr.Literal(True),
            operator=Token(Tok.AND, "and"),
            right=expr.Literal(False),
        )
        assert result == expected
        assert offset == 3

    def test_multiple_and(self):
        tokens = [
            Token(Tok.TRUE, "true"),
            Token(Tok.AND, "and"),
            Token(Tok.FALSE, "false"),
            Token(Tok.AND, "and"),
            Token(Tok.FALSE, "false"),
        ]
        result, offset = parser.and_expression(tokens, 0)
        expected = expr.Logical(
            left=expr.Literal(True),
            operator=Token(Tok.AND, "and"),
            right=expr.Logical(
                left=expr.Literal(False),
                operator=Token(Tok.AND, "and"),
                right=expr.Literal(False),
            ),
        )
        assert result == expected
        assert offset == 5

    def test_equality(self):
        """Returns an equality expression if cannot match `and`"""
        tokens = [
            Token(Tok.TRUE, "true"),
            Token(Tok.EQUAL_EQUAL, "=="),
            Token(Tok.FALSE, "false"),
        ]
        result, offset = parser.and_expression(tokens, 0)
        expected = expr.Binary(
            left=expr.Literal(True),
            operator=Token(Tok.EQUAL_EQUAL, "=="),
            right=expr.Literal(False),
        )
        assert result == expected
        assert offset == 3


class TestOrExpression:
    """Unit tests for `or_expression`."""

    def test_simple_or(self):
        tokens = [
            Token(Tok.TRUE, "true"),
            Token(Tok.OR, "or"),
            Token(Tok.FALSE, "false"),
        ]
        result, offset = parser.or_expression(tokens, 0)
        expected = expr.Logical(
            left=expr.Literal(True),
            operator=Token(Tok.OR, "or"),
            right=expr.Literal(False),
        )
        assert result == expected
        assert offset == 3

    def test_multiple_or(self):
        tokens = [
            Token(Tok.TRUE, "true"),
            Token(Tok.OR, "or"),
            Token(Tok.FALSE, "false"),
            Token(Tok.OR, "or"),
            Token(Tok.TRUE, "true"),
        ]
        result, offset = parser.or_expression(tokens, 0)
        expected = expr.Logical(
            left=expr.Literal(True),
            operator=Token(Tok.OR, "or"),
            right=expr.Logical(
                left=expr.Literal(False),
                operator=Token(Tok.OR, "or"),
                right=expr.Literal(True),
            ),
        )
        assert result == expected
        assert offset == 5

    def test_and(self):
        """Differs to `and` if cannot match an OR token."""
        tokens = [
            Token(Tok.FALSE, "false"),
            Token(Tok.AND, "and"),
            Token(Tok.TRUE, "true"),
        ]
        result, offset = parser.or_expression(tokens, 0)
        expected = expr.Logical(
            left=expr.Literal(False),
            operator=Token(Tok.AND, "and"),
            right=expr.Literal(True),
        )
        assert result == expected
        assert offset == 3


def test_var_declaration_uninitialised_expression():
    tokens = [Token(Tok.IDENTIFIER, "x"), Token(Tok.SEMICOLON, ";")]
    result, offset = parser.var_declaration(tokens, 0)
    assert result == stmt.Var(Token(Tok.IDENTIFIER, "x"), None)
    assert offset == 2


def test_var_declaration_initialised_expression():
    tokens = [
        Token(Tok.IDENTIFIER, "cats"),
        Token(Tok.EQUAL, "="),
        Token(Tok.STRING, '"meow"', "meow"),
        Token(Tok.SEMICOLON, ";"),
    ]
    result, offset = parser.var_declaration(tokens, 0)
    assert result == stmt.Var(
        Token(Tok.IDENTIFIER, "cats"),
        expr.Literal("meow"),
    )
    assert offset == 4


def test_var_declaration_case_no_identifier():
    """
    `var_declaration` raises an error when not given an identifier token.
    """
    tokens = [Token(Tok.NUMBER, "5", 5.0), Token(Tok.SEMICOLON, ";")]
    with pytest.raises(parser.ParserError):
        _ = parser.var_declaration(tokens, 0)


class TestVarDeclaration:
    """Unit tests for `var_declaration`"""

    def test_no_semicolon(self):
        """Raises an error when the statement does not end in a semicolon."""
        tokens = [
            Token(Tok.IDENTIFIER, "z"),
            Token(Tok.EQUAL, "="),
            Token(Tok.NUMBER, "1", 1.0),
        ]
        with pytest.raises(parser.ParserError):
            _ = parser.var_declaration(tokens, 0)


@pytest.mark.parametrize(
    "tokens,expected",
    [
        ([Token(Tok.SEMICOLON, ";")], None),
        ([Token(Tok.EQUAL, "="), Token(Tok.NUMBER, "5", 5.0)], expr.Literal(5.0)),
    ],
)
def test_var_initialiser(
    tokens: list[Token],
    expected: tuple[expr.Expr | None, int],
):
    """
    Should return None when token is `Tok.SEMICOLON`.
    Should return an expression when token is `Tok.EQUAL`.
    """
    result, _ = parser.var_initialiser_expression(tokens, 0)
    assert result == expected


def test_var_initialiser_exception():
    """
    Token at `offset` should be of type `Tok.EQUAL` or `Tok.SEMICOLON`
    """
    tokens = [Token(Tok.NUMBER, "4", 4.0)]
    with pytest.raises(parser.ParserError):
        _ = parser.var_initialiser_expression(tokens, 0)


def test_print_statement():
    tokens = [
        Token(Tok.STRING, '"hello world"', "hello world"),
        Token(Tok.SEMICOLON, ";"),
    ]
    expected = stmt.PrintStmt(expr.Literal("hello world"))
    result, offset = parser.print_statement(tokens, 0)
    assert result == expected
    assert offset == 2


def test_bodmas():
    tokens = [
        Token(Tok.NUMBER, "4.0", 4.0),
        Token(Tok.PLUS, "+"),
        Token(Tok.NUMBER, "3.0", 3.0),
        Token(Tok.SLASH, "/"),
        Token(Tok.NUMBER, "2.0", 2.0),
        Token(Tok.MINUS, "-"),
        Token(Tok.NUMBER, "1.0", 1.0),
    ]
    expected = expr.Binary(
        left=expr.Literal(4.0),
        operator=Token(Tok.PLUS, "+"),
        right=expr.Binary(
            left=expr.Binary(
                left=expr.Literal(3.0),
                operator=Token(Tok.SLASH, "/"),
                right=expr.Literal(2.0),
            ),
            operator=Token(Tok.MINUS, "-"),
            right=expr.Literal(1.0),
        ),
    )
    result, offset = parser.get_expression(tokens, 0)
    assert result == expected
    assert offset == 7


def test_repeated_addition():
    tokens = [
        Token(Tok.NUMBER, "4.0", 4.0),
        Token(Tok.PLUS, "+"),
        Token(Tok.NUMBER, "3.0", 3.0),
        Token(Tok.PLUS, "+"),
        Token(Tok.NUMBER, "2.0", 2.0),
        Token(Tok.PLUS, "+"),
        Token(Tok.NUMBER, "1.0", 1.0),
    ]
    expected = expr.Binary(
        left=expr.Literal(4.0),
        operator=Token(Tok.PLUS, "+"),
        right=expr.Binary(
            left=expr.Literal(3.0),
            operator=Token(Tok.PLUS, "+"),
            right=expr.Binary(
                left=expr.Literal(2.0),
                operator=Token(Tok.PLUS, "+"),
                right=expr.Literal(1.0),
            ),
        ),
    )
    result, _ = parser.get_expression(tokens, 0)
    assert result == expected


def test_incomplete_expressions():
    tokens = [
        Token(Tok.STRING, '"cat"', "cat"),
        Token(Tok.GREATER, ">"),
    ]
    expected = expr.Binary(
        left=expr.Literal("cat"),
        operator=Token(Tok.GREATER, ">"),
        right=expr.Empty(),
    )
    result, _ = parser.get_expression(tokens, 0)
    assert result == expected


def test_equality_expression():
    tokens = [
        Token(Tok.STRING, '"cat"', "cat"),
        Token(Tok.EQUAL_EQUAL, "=="),
        Token(Tok.STRING, '"dog"', "dog"),
    ]
    expected = expr.Binary(
        left=expr.Literal("cat"),
        operator=Token(Tok.EQUAL_EQUAL, "=="),
        right=expr.Literal("dog"),
    )
    result, _ = parser.equality_expession(tokens, 0)
    assert result == expected


def test_comparison_expression():
    tokens = [
        Token(Tok.NUMBER, "7", 7),
        Token(Tok.GREATER, ">"),
        Token(Tok.NUMBER, "5", 5),
    ]
    expected = expr.Binary(
        left=expr.Literal(7),
        operator=Token(Tok.GREATER, ">"),
        right=expr.Literal(5),
    )
    result, offset = parser.comparison_expression(tokens, 0)
    assert result == expected
    assert offset == 3


def test_term_expression():
    tokens = [
        Token(Tok.NUMBER, "42", 42),
        Token(Tok.PLUS, "+"),
        Token(Tok.NUMBER, "7", 7),
    ]
    expected = expr.Binary(
        left=expr.Literal(42),
        operator=Token(Tok.PLUS, "+"),
        right=expr.Literal(7),
    )
    result, offset = parser.term_expression(tokens, 0)
    assert result == expected
    assert offset == 3


@pytest.mark.parametrize(
    "tokens,expected,exp_offset",
    [
        # Simple case
        (
            [
                Token(Tok.NUMBER, "5", 5),
                Token(Tok.STAR, "*"),
                Token(Tok.NUMBER, "12", 12),
            ],
            expr.Binary(
                left=expr.Literal(5),
                operator=Token(Tok.STAR, "*"),
                right=expr.Literal(12),
            ),
            3,
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
                    right=expr.Literal(3),
                ),
                operator=Token(Tok.SLASH, "/"),
                right=expr.Literal(4),
            ),
            4,
        ),
    ],
)
def test_factor_expression(tokens: list[Token], expected: expr.Binary, exp_offset: int):
    result, offset = parser.factor_expression(tokens, 0)
    assert result == expected
    assert offset == exp_offset


@pytest.mark.parametrize(
    "tokens,exp_expression,exp_offset",
    [
        (
            [Token(Tok.MINUS, "-", None), Token(Tok.NUMBER, "12", 12)],
            expr.Unary(
                Token(Tok.MINUS, "-", None),
                expr.Literal(
                    12,
                ),
            ),
            2,
        )
    ],
)
def test_unary_expression(
    tokens: list[Token], exp_expression: expr.Unary, exp_offset: int
):
    result, offset = parser.unary_expression(tokens, 0)
    assert result == exp_expression
    assert offset == exp_offset


@pytest.mark.parametrize(
    "tokens,exp_expression,exp_offset",
    [
        ([Token(Tok.NUMBER, "3.14", 3.14)], expr.Literal(3.14), 1),
        ([Token(Tok.STRING, '"cats"', "cats")], expr.Literal("cats"), 1),
        ([Token(Tok.NIL, "Nil", None)], expr.Literal(None), 1),
        ([Token(Tok.TRUE, "true", None)], expr.Literal(True), 1),
        ([Token(Tok.FALSE, "false", None)], expr.Literal(False), 1),
    ],
)
def test_primary_expression(
    tokens: list[Token], exp_expression: expr.Literal, exp_offset: int
):
    result, offset = parser.primary_expression(tokens, 0)
    assert result == exp_expression and offset == exp_offset


@pytest.mark.parametrize(
    "tokens,exp_expression,exp_offset",
    [
        # Basic test case
        (
            [
                Token(Tok.LEFT_PAREN, "(", None),
                Token(Tok.NUMBER, "7", 7),
                Token(Tok.RIGHT_PAREN, ")", None),
            ],
            expr.Grouping(expr.Literal(7)),
            3,
        )
    ],
)
def test_grouping_expression(
    tokens: list[Token], exp_expression: expr.Grouping, exp_offset: int
):
    result, offset = parser.grouping_expression(tokens, 1)
    assert result == exp_expression
    # assert offset == exp_offset
