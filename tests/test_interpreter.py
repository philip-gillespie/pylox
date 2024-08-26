"""
test_interpreter.py

Unit tests for interpreter.py
"""

import pytest
from pylox import interpreter
from pylox import stmt
from pylox.environment import Environment
from pylox.tokens import Token, Tok
from pylox import expr


class TestInterpret:
    """Unit tests for `interpret` function"""

    def test_print_statement(self):
        statements = [stmt.PrintStmt(expr.Literal("hello world"))]
        env = Environment()
        result = interpreter.interpret(statements, env)
        assert result == env

    def test_var_assigment(self):
        statements = [
            stmt.Var(
                Token(Tok.IDENTIFIER, "x", "x"),
                expr.Literal(5.0),
            )
        ]
        env = Environment()
        expected = env.get_copy_with("x", 5.0)
        result = interpreter.interpret(statements, env)
        assert result == expected


class TestInterpretBlockStatement:
    """Unit Tests for interpret_block_statement."""

    def test_inner_environment(self):
        """Inner environment is not preserved when moving out of a block."""
        statement = stmt.Block(
            statements=[
                stmt.Var(Token(Tok.IDENTIFIER, "x"), expr.Literal(5.0)),
                stmt.PrintStmt(
                    expr.Variable(
                        Token(Tok.IDENTIFIER, "x"),
                    ),
                ),
            ],
        )
        result: Environment = interpreter.interpret_block_statement(
            statement, Environment()
        )
        assert result == Environment()

    def test_outer_environment(self):
        """Blocks envlosing environment should be preserved."""
        statement = stmt.Block(
            statements=[
                stmt.Var(Token(Tok.IDENTIFIER, "x"), expr.Literal(5.0)),
                stmt.PrintStmt(
                    expr.Variable(
                        Token(Tok.IDENTIFIER, "x"),
                    ),
                ),
            ],
        )
        env = Environment({"y": 3.0})
        result: Environment = interpreter.interpret_block_statement(statement, env)
        assert result == env

    def test_update_enclosing_env(self):
        statement = stmt.Block(
            statements=[
                stmt.Expression(
                    expr.Assign(Token(Tok.IDENTIFIER, "x"), expr.Literal(5.0))
                ),
            ],
        )
        env = Environment({"x": 3.0})
        result: Environment = interpreter.interpret_block_statement(
            statement=statement,
            env=env,
        )
        expected = Environment({"x": 5.0})
        assert result == expected


class TestInterpretWhileStatement:
    """Unit tests for `interpret_while_statement`."""

    def test_while(self):
        statement = stmt.While(
            condition=expr.Binary(
                left=expr.Variable(name=Token(Tok.IDENTIFIER, "x")),
                operator=Token(Tok.LESS, "<"),
                right=expr.Literal(5.0),
            ),
            body=stmt.Expression(
                expr.Assign(
                    name=Token(Tok.IDENTIFIER, "x"),
                    value=expr.Binary(
                        left=expr.Variable(name=Token(Tok.IDENTIFIER, "x")),
                        operator=Token(Tok.PLUS, "+"),
                        right=expr.Literal(1.0),
                    ),
                )
            ),
        )
        env = Environment({"x": 1.0})
        result = interpreter.interpret_while_statement(statement, env)
        expected = Environment({"x": 5.0})
        assert result == expected


class TestEvaluate:
    """Unit tests for `evaluate`."""

    def test_logical(self):
        """Evaluate `expr.Logical`."""
        expression = expr.Logical(
            left=expr.Literal(0.0),
            operator=Token(Tok.OR, "or"),
            right=expr.Literal(False),
        )
        result, env = interpreter.evaluate(expression, Environment())
        assert result == False
        assert env == Environment()


class TestEvaluateLogical:
    """Unit tests for `evaluate_logical`."""

    def test_logical_or(self):
        """Returns correct response for logical or."""
        expression = expr.Logical(
            left=expr.Literal(1.0),
            operator=Token(Tok.OR, "or"),
            right=expr.Literal(False),
        )
        result, env = interpreter.evaluate_logical(expression, Environment())
        assert result == 1.0
        assert env == Environment()

    def test_logical_and(self):
        """Returns Correct Response for logical or."""
        expression = expr.Logical(
            left=expr.Literal(1.0),
            operator=Token(Tok.AND, "and"),
            right=expr.Literal(False),
        )
        result, env = interpreter.evaluate_logical(expression, Environment())
        assert result == False
        assert env == Environment()


class TestEvaluateLogicalOr:
    """Unit tests for `evaluate_logical_or`"""

    def test_left_true(self):
        expression = expr.Logical(
            left=expr.Literal(True),
            operator=Token(Tok.OR, "or"),
            right=expr.Literal(False),
        )
        result, env = interpreter.evaluate_logical_or(expression, Environment())
        expected = True
        assert result == expected
        assert env == Environment()

    def test_right_true(self):
        expression = expr.Logical(
            left=expr.Literal(False),
            operator=Token(Tok.OR, "or"),
            right=expr.Literal(True),
        )
        result, env = interpreter.evaluate_logical_or(expression, Environment())
        expected = True
        assert result == expected
        assert env == Environment()

    def test_both_false(self):
        expression = expr.Logical(
            left=expr.Literal(False),
            operator=Token(Tok.OR, "or"),
            right=expr.Literal(False),
        )
        result, env = interpreter.evaluate_logical_or(expression, Environment())
        expected = False
        assert result == expected
        assert env == Environment()

    def test_both_true(self):
        expression = expr.Logical(
            left=expr.Literal(True),
            operator=Token(Tok.OR, "or"),
            right=expr.Literal(True),
        )
        result, env = interpreter.evaluate_logical_or(expression, Environment())
        expected = True
        assert result == expected
        assert env == Environment()

    def test_left_preference(self):
        expression = expr.Logical(
            left=expr.Literal(1.0),
            operator=Token(Tok.OR, "or"),
            right=expr.Literal(True),
        )
        result, env = interpreter.evaluate_logical_or(expression, Environment())
        expected = 1.0
        assert result == expected
        assert env == Environment()


class TestEvaluateLogicalAnd:
    """Unit tests for `evaluate_logical_and`."""

    def test_left_true(self):
        """Return false when only left is true"""
        expression = expr.Logical(
            left=expr.Literal(True),
            operator=Token(Tok.AND, "and"),
            right=expr.Literal(False),
        )
        result, env = interpreter.evaluate_logical_and(expression, Environment())
        expected = False
        assert result == expected
        assert env == Environment()

    def test_right_true(self):
        """Return False when only right is true."""
        expression = expr.Logical(
            left=expr.Literal(False),
            operator=Token(Tok.AND, "and"),
            right=expr.Literal(True),
        )
        result, env = interpreter.evaluate_logical_and(expression, Environment())
        expected = False
        assert result == expected
        assert env == Environment()

    def test_both_false(self):
        """Return False when both are false."""
        expression = expr.Logical(
            left=expr.Literal(False),
            operator=Token(Tok.AND, "and"),
            right=expr.Literal(False),
        )
        result, env = interpreter.evaluate_logical_and(expression, Environment())
        expected = False
        assert result == expected
        assert env == Environment()

    def test_both_true(self):
        """Return True when both values return True."""
        expression = expr.Logical(
            left=expr.Literal(True),
            operator=Token(Tok.AND, "and"),
            right=expr.Literal(True),
        )
        result, env = interpreter.evaluate_logical_and(expression, Environment())
        expected = True
        assert result == expected
        assert env == Environment()

    def test_left_priotity(self):
        """Returns left value when left is False."""
        expression = expr.Logical(
            left=expr.Literal(0.0),
            operator=Token(Tok.AND, "and"),
            right=expr.Literal(False),
        )
        result, env = interpreter.evaluate_logical_and(expression, Environment())
        expected = 0.0
        assert result == expected
        assert env == Environment()


@pytest.mark.parametrize(
    "item, expected",
    [
        (True, "true"),
        (False, "false"),
        (None, "nil"),
        ("cats", "cats"),
        (5.0, "5.0"),
        (3.14, "3.14"),
        (1.0, "1.0"),
    ],
)
def test_stringify(item: object, expected: str):
    result = interpreter.stringify(item)
    assert result == expected


@pytest.mark.parametrize(
    "expression,expected",
    [
        (expr.Literal(value=2), 2),
        (expr.Literal(value="hello"), "hello"),
        (expr.Literal(value=None), None),
        (expr.Literal(value=True), True),
        (expr.Literal(value=False), False),
    ],
)
def test_interpret_literal_expression(
    expression: expr.Literal,
    expected: object,
):
    env = Environment()
    result, new_env = interpreter.interpret_literal(expression, env)
    assert result == expected
    assert env == new_env


def test_interpret_grouping_expression():
    env = Environment()
    expression = expr.Grouping(expr.Literal(5))
    result, new_env = interpreter.interpret_grouping(expression, env)
    expected = 5
    assert result == expected
    assert env == new_env


@pytest.mark.parametrize(
    "expression,expected",
    [
        (expr.Unary(Token(Tok.MINUS, "-"), expr.Literal(float(7))), -7),
        (expr.Unary(Token(Tok.BANG, "!"), expr.Literal(True)), False),
        (expr.Unary(Token(Tok.BANG, "!"), expr.Literal(None)), True),
        (expr.Unary(Token(Tok.BANG, "!"), expr.Literal(float(1))), False),
        (expr.Unary(Token(Tok.BANG, "!"), expr.Literal("cats")), False),
    ],
)
def test_unary_operator(expression: expr.Unary, expected: object):
    env = Environment()
    result, new_env = interpreter.interpret_unary(expression, env)
    assert result == expected
    assert env == new_env


@pytest.mark.parametrize(
    "expression",
    [
        expr.Unary(
            operator=Token(Tok.MINUS, "-"),
            right=expr.Literal("dogs"),
        ),
        expr.Unary(
            operator=Token(Tok.STAR, "*"),
            right=expr.Literal(5),
        ),
    ],
)
def test_unary_runtime_error(expression: expr.Unary):
    with pytest.raises(interpreter.RuntimeError):
        _ = interpreter.interpret_unary(expression, Environment())


@pytest.mark.parametrize(
    "value,expected",
    [
        (False, False),
        (True, True),
        (None, False),
        (9876, True),
        ("hello", True),
    ],
)
def test_is_truthy(value: object, expected: bool):
    result = interpreter.is_truthy(value)
    assert result == expected


@pytest.mark.parametrize(
    "expression,expected",
    [
        (
            expr.Binary(
                left=expr.Literal(float(5)),
                operator=Token(Tok.MINUS, "-"),
                right=expr.Literal(float(3)),
            ),
            float(5) - float(3),
        ),
        (
            expr.Binary(
                left=expr.Literal(float(9)),
                operator=Token(Tok.SLASH, "/"),
                right=expr.Literal(float(2)),
            ),
            float(9) / float(2),
        ),
        (
            expr.Binary(
                left=expr.Literal(float(9)),
                operator=Token(Tok.GREATER, ">"),
                right=expr.Literal(float(2)),
            ),
            True,
        ),
        (
            expr.Binary(
                left=expr.Literal("hello "),
                operator=Token(Tok.PLUS, "+"),
                right=expr.Literal("world!"),
            ),
            "hello world!",
        ),
        (
            expr.Binary(
                left=expr.Literal("cats"),
                operator=Token(Tok.BANG_EQUAL, "!="),
                right=expr.Literal("cats"),
            ),
            False,
        ),
        (
            expr.Binary(
                left=expr.Literal("cats"),
                operator=Token(Tok.EQUAL_EQUAL, "=="),
                right=expr.Literal("cats"),
            ),
            True,
        ),
    ],
)
def test_binary_expression(expression: expr.Binary, expected: object):
    environment = Environment()
    result, output_env = interpreter.interpret_binary(expression, environment)
    assert result == expected
    assert environment == output_env


def test_binary_expression_error():
    """
    A runtime error is raised when an unrecognised operator is present.
    """
    # Nonsense expression
    expression = expr.Binary(
        left=expr.Literal(3.0),
        operator=Token(Tok.FUN, "fun"),
        right=expr.Literal(5.0),
    )
    with pytest.raises(interpreter.RuntimeError):
        interpreter.interpret_binary(expression, Environment())


@pytest.mark.parametrize(
    "left,operator,right,expected",
    [
        (7.0, Token(Tok.MINUS, "-"), 2.0, 5.0),
        (7.0, Token(Tok.SLASH, "/"), 2.0, 3.5),
        (7.0, Token(Tok.STAR, "*"), 2.0, 14.0),
        (7.0, Token(Tok.GREATER, ">"), 2.0, True),
        (7.0, Token(Tok.GREATER_EQUAL, ">="), 2.0, True),
        (7.0, Token(Tok.GREATER_EQUAL, ">="), 7.0, True),
        (7.0, Token(Tok.GREATER_EQUAL, ">="), 9.0, False),
        (7.0, Token(Tok.LESS, "<"), 2.0, False),
        (1.0, Token(Tok.LESS, "<"), 2.0, True),
        (1.0, Token(Tok.LESS_EQUAL, "<="), 2.0, True),
        (2.0, Token(Tok.LESS_EQUAL, "<="), 2.0, True),
        (5.0, Token(Tok.LESS_EQUAL, "<="), 2.0, False),
    ],
)
def test_interpret_binary_numeric(
    left: object, operator: Token, right: object, expected: object
):
    result = interpreter.interpret_binary_numeric(left, operator, right)
    assert result == expected


def test_interpret_binary_numeric_error():
    left = "cats"
    right = 3.0
    operator = Token(Tok.SLASH, "/")
    with pytest.raises(interpreter.RuntimeError):
        interpreter.interpret_binary_numeric(left, operator, right)


@pytest.mark.parametrize(
    "left,right,expected",
    [
        (float(2), float(3), float(2) + float(3)),
        ("hello ", "world!", "hello world!"),
    ],
)
def test_add(left: object, right: object, expected: object):
    operator = Token(Tok.PLUS, "+")
    result = interpreter.add(left, operator, right)
    assert result == expected


def test_add_error():
    operator = Token(Tok.PLUS, "+")
    with pytest.raises(interpreter.RuntimeError):
        interpreter.add(float(2), operator, "cats")


@pytest.mark.parametrize(
    "left,right,expected",
    [
        (None, None, True),
        (None, "cats", False),
        (1.0, 1.0, True),
    ],
)
def test_is_equal(left: object, right: object, expected):
    result = interpreter.is_equal(left, right)
    assert result == expected
