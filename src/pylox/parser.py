"""parser.py"""

from typing import Sequence
from pylox import stmt
from pylox.tokens import Tok, Token

from pylox import expr


class ParserError(Exception):
    def __init__(self, token: Token | None, message: str):
        self.token = token
        self.message = message


def parse(tokens: list[Token]) -> Sequence[stmt.Stmt]:
    statements = []
    i = 0
    while i < len(tokens):
        statement, i = get_statement(tokens, i)
        statements.append(statement)
    return statements


def get_statement(tokens: list[Token], offset: int) -> tuple[stmt.Stmt, int]:
    token, token_offset = get_token(tokens, offset)
    if token.token_type == Tok.VAR:
        return var_declaration(tokens, token_offset)
    if token.token_type == Tok.PRINT:
        return print_statement(tokens, token_offset)
    if token.token_type == Tok.LEFT_BRACE:
        return block_statement(tokens, token_offset)
    if token.token_type == Tok.IF:
        return if_statement(tokens, token_offset)
    if token.token_type == Tok.WHILE:
        return while_statement(tokens, token_offset)
    if token.token_type == Tok.FOR:
        return for_statement(tokens, token_offset)
    return expression_statement(tokens, offset)


def var_declaration(tokens: list[Token], offset: int) -> tuple[stmt.Stmt, int]:
    name, name_offset = get_token(tokens, offset)
    if name.token_type != Tok.IDENTIFIER:
        raise ParserError(name, "Expect variable name.")
    initialiser, init_offset = var_initialiser_expression(tokens, name_offset)
    semicolon, semicolon_offset = get_token(tokens, init_offset)
    if semicolon.token_type != Tok.SEMICOLON:
        raise ParserError(semicolon, "Expect `;` after variable declaration")
    return stmt.Var(name, initialiser), semicolon_offset


def var_initialiser_expression(
    tokens: list[Token], offset: int
) -> tuple[expr.Expr | None, int]:
    equal, equal_offset = get_token(tokens, offset)
    if equal.token_type == Tok.SEMICOLON:
        return None, offset
    if equal.token_type != Tok.EQUAL:
        raise ParserError(equal, "Expect `;` or `=` after variable name.")
    initialiser, init_offset = get_expression(tokens, equal_offset)
    return initialiser, init_offset


def print_statement(tokens: list[Token], offset: int) -> tuple[stmt.PrintStmt, int]:
    """
    Return a print statement, and new offset from a list of tokens.
    Assumes that the `Token` at position `offset` is a print token.
    """
    expression, expr_offset = get_expression(tokens, offset)
    semicolon, semicolon_offset = get_token(tokens, expr_offset)
    if semicolon.token_type != Tok.SEMICOLON:
        raise ParserError(semicolon, "Expect `;` after expression.")
    return stmt.PrintStmt(expression), semicolon_offset


def block_statement(tokens: list[Token], offset: int) -> tuple[stmt.Block, int]:
    statements: list[stmt.Stmt] = []
    right_brace, brace_offset = get_token(tokens, offset)
    while (brace_offset < len(tokens)) and (right_brace.token_type != Tok.RIGHT_BRACE):
        statement, i = get_statement(tokens, brace_offset)
        right_brace, brace_offset = get_token(tokens, i)
        statements.append(statement)
    if right_brace.token_type != Tok.RIGHT_BRACE:
        raise ParserError(right_brace, "Expect `}` after block.")
    return stmt.Block(statements), brace_offset


def if_statement(tokens: list[Token], offset: int) -> tuple[stmt.IfStmt, int]:
    left_paren, lp_offset = get_token(tokens, offset)
    if left_paren.token_type != Tok.LEFT_PAREN:
        raise ParserError(left_paren, "Expect `(` after `if`.")
    condition, condition_offset = get_expression(tokens, lp_offset)
    right_paren, rp_offset = get_token(tokens, condition_offset)
    if right_paren.token_type != Tok.RIGHT_PAREN:
        raise ParserError(right_paren, "Expect `)` after if condition")
    then_branch, then_offset = get_statement(tokens, rp_offset)
    else_token, else_offset = get_token(tokens, then_offset)
    if else_token.token_type != Tok.ELSE:
        return (
            stmt.IfStmt(
                condition=condition,
                then_branch=then_branch,
                else_branch=None,
            ),
            then_offset,
        )

    else_branch, eb_offset = get_statement(tokens, else_offset)
    return (
        stmt.IfStmt(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
        ),
        eb_offset,
    )


def while_statement(tokens: list[Token], offset: int) -> tuple[stmt.While, int]:
    left_paren, lp_offset = get_token(tokens, offset)
    if left_paren.token_type != Tok.LEFT_PAREN:
        raise ParserError(left_paren, "Expect `(` after `while`.")
    condition, condition_offset = get_expression(tokens, lp_offset)
    right_paren, rp_offset = get_token(tokens, condition_offset)
    if right_paren.token_type != Tok.RIGHT_PAREN:
        raise ParserError(right_paren, "Expect `)` after while condition.")
    body, body_offset = get_statement(tokens, rp_offset)
    return stmt.While(condition=condition, body=body), body_offset


def for_statement(tokens: list[Token], offset: int) -> tuple[stmt.Stmt, int]:
    """Parse a for clause into a while loop."""
    left_paren, lp_offset = get_token(tokens, offset)
    if left_paren.token_type != Tok.LEFT_PAREN:
        raise ParserError(left_paren, "Expect `(` after `for`.")
    init, init_offset = for_statement_initialiser(tokens, lp_offset)
    condition, condition_offset = for_statement_condition(tokens, init_offset)
    inc, inc_offset = for_statement_increment(tokens, condition_offset)
    body, body_offset = get_statement(tokens, inc_offset)
    statement = _assemble_while_statement(init, condition, inc, body)
    return statement, body_offset


def for_statement_initialiser(
    tokens: list[Token],
    offset: int,
) -> tuple[stmt.Stmt | None, int]:
    token, token_offset = get_token(tokens, offset)
    if token.token_type == Tok.SEMICOLON:
        return None, token_offset
    if token.token_type == Tok.VAR:
        return var_declaration(tokens, token_offset)
    return expression_statement(tokens, offset)


def for_statement_condition(
    tokens: list[Token],
    offset: int,
) -> tuple[expr.Expr | None, int]:
    """Parse the condition of a for loop."""
    token, token_offset = get_token(tokens, offset)
    if token.token_type == Tok.SEMICOLON:
        return None, token_offset
    condition, condition_offset = get_expression(tokens, offset)
    semicolon, semicolon_offset = get_token(tokens, condition_offset)
    if semicolon.token_type != Tok.SEMICOLON:
        raise ParserError(semicolon, "Expect `;` after for loop condition.")
    return condition, semicolon_offset


def for_statement_increment(
    tokens: list[Token],
    offset: int,
) -> tuple[expr.Expr | None, int]:
    """Parse the increment of a for loop."""
    token, token_offset = get_token(tokens, offset)
    if token.token_type == Tok.RIGHT_PAREN:
        return None, token_offset
    expression, expression_offset = get_expression(tokens, offset)
    right_paren, rp_offset = get_token(tokens, expression_offset)
    if right_paren.token_type != Tok.RIGHT_PAREN:
        raise ParserError(right_paren, "Expect `)` after loop increment.")
    return expression, rp_offset


def _assemble_while_statement(
    initialiser: stmt.Stmt | None,
    condition: expr.Expr | None,
    increment: expr.Expr | None,
    body: stmt.Stmt,
) -> stmt.Stmt:
    statement = body
    if increment is not None:
        statement = stmt.Block([body, stmt.Expression(increment)])
    if condition is not None:
        statement = stmt.While(condition=condition, body=statement)
    if initialiser is not None:
        statement = stmt.Block([initialiser, statement])
    return statement


def expression_statement(
    tokens: list[Token], offset: int
) -> tuple[stmt.Expression, int]:
    expr, i = get_expression(tokens, offset)
    token, token_offset = get_token(tokens, i)
    if token.token_type != Tok.SEMICOLON:
        raise ParserError(token, "Expect `;` after expression.")
    return stmt.Expression(expr), token_offset


def get_expression(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    expr, offset = assignment_expression(tokens, offset)
    return expr, offset


def assignment_expression(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    """
    Return an assignment expression if possible.
    Otherwise next most important.
    """
    expression, expr_offset = or_expression(tokens, offset)
    equal, equal_offset = get_token(tokens, expr_offset)
    if equal.token_type == Tok.EQUAL:
        value, output_offset = assignment_expression(tokens, equal_offset)
        if isinstance(expression, expr.Variable):
            return expr.Assign(expression.name, value), output_offset
        raise ParserError(equal, "Invalid assignment target.")
    return expression, expr_offset


def or_expression(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    left, left_offset = and_expression(tokens, offset)
    or_token, or_offset = get_token(tokens, left_offset)
    if or_token.token_type != Tok.OR:
        return left, left_offset
    right, right_offset = or_expression(tokens, or_offset)
    return (
        expr.Logical(left=left, operator=or_token, right=right),
        right_offset,
    )


def and_expression(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    left, left_offset = equality_expession(tokens, offset)
    and_token, and_offset = get_token(tokens, left_offset)
    if and_token.token_type != Tok.AND:
        return left, left_offset
    right, right_offset = and_expression(tokens, and_offset)
    return (
        expr.Logical(left=left, operator=and_token, right=right),
        right_offset,
    )


def equality_expession(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    left, left_offset = comparison_expression(tokens, offset)
    token, token_offset = get_token(tokens, left_offset)
    if token.token_type not in [Tok.BANG_EQUAL, Tok.EQUAL_EQUAL]:
        return left, left_offset
    right, right_offset = comparison_expression(tokens, token_offset)
    return (
        expr.Binary(
            left=left,
            operator=token,
            right=right,
        ),
        right_offset,
    )


def comparison_expression(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    left, left_offset = term_expression(tokens, offset)
    operator, operator_offset = get_token(tokens, left_offset)
    operators = [Tok.GREATER, Tok.GREATER_EQUAL, Tok.LESS, Tok.LESS_EQUAL]
    if operator.token_type not in operators:
        return left, left_offset
    right, output_offset = term_expression(tokens, operator_offset)
    return (
        expr.Binary(
            left=left,
            operator=operator,
            right=right,
        ),
        output_offset,
    )


def term_expression(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    left, left_offset = factor_expression(tokens, offset)
    operator, operator_offset = get_token(tokens, left_offset)
    if operator.token_type not in [Tok.PLUS, Tok.MINUS]:
        return left, left_offset
    right, output_offset = term_expression(tokens, operator_offset)
    return (
        expr.Binary(
            left=left,
            operator=operator,
            right=right,
        ),
        output_offset,
    )


def factor_expression(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    left, left_offset = unary_expression(tokens, offset)
    operator, operator_offset = get_token(tokens, left_offset)
    if operator.token_type not in [Tok.STAR, Tok.SLASH]:
        return left, left_offset
    right, output_offset = unary_expression(tokens, operator_offset)
    return (
        expr.Binary(
            left=left,
            operator=operator,
            right=right,
        ),
        output_offset,
    )


def unary_expression(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    operator, operator_offset = get_token(tokens, offset)
    if operator.token_type in [Tok.BANG, Tok.MINUS]:
        expression, expr_offset = unary_expression(tokens, operator_offset)
        return (
            expr.Unary(
                operator=operator,
                right=expression,
            ),
            expr_offset,
        )
    return call_expression(tokens, offset)


def call_expression(tokens, offset) -> tuple[expr.Expr, int]:
    expression, expr_offset = primary_expression(tokens, offset)
    left_paren, lp_offset = get_token(tokens, expr_offset)
    if left_paren.token_type != Tok.LEFT_PAREN:
        return expression, expr_offset
    arguments, arg_offset = _call_expression_arguments(tokens, lp_offset)
    return expr.Call(expression, left_paren, arguments), arg_offset


def _call_expression_arguments(
    tokens: list[Token], offset: int
) -> tuple[list[expr.Expr], int]:
    arguments: list[expr.Expr] = list()
    token, token_offset = get_token(tokens, offset)
    if token.token_type == Tok.RIGHT_PAREN:
        return arguments, token_offset
    argument, arg_offset = get_expression(tokens, offset)
    arguments.append(argument)
    token, token_offset = get_token(tokens, arg_offset)
    while token.token_type == Tok.COMMA:
        argument, arg_offset = get_expression(tokens, token_offset)
        arguments.append(argument)
        token, token_offset = get_token(tokens, arg_offset)
        if len(arguments) > 255:
            raise ParserError(token, "Cannot have more than 255 arguments.")
    if token.token_type != Tok.RIGHT_PAREN:
        raise ParserError(token, "Expect `)` after arguments.")
    return arguments, token_offset


def primary_expression(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    token, token_offset = get_token(tokens, offset)
    match token.token_type:
        case Tok.NUMBER | Tok.STRING | Tok.NIL:
            return expr.Literal(token.value), token_offset
        case Tok.TRUE:
            return expr.Literal(True), token_offset
        case Tok.FALSE:
            return expr.Literal(False), token_offset
        case Tok.LEFT_PAREN:
            return grouping_expression(tokens, token_offset)
        case Tok.IDENTIFIER:
            return expr.Variable(token), token_offset
    return expr.Empty(), token_offset


def grouping_expression(tokens: list[Token], offset: int) -> tuple[expr.Expr, int]:
    next_expression, new_offset = get_expression(tokens, offset)
    token, token_offset = get_token(tokens, new_offset)
    if token.token_type != Tok.RIGHT_PAREN:
        raise ParserError(token, "Expect ')' after expression.")
    return expr.Grouping(next_expression), token_offset



def get_token(tokens: list[Token], i: int) -> tuple[Token, int]:
    try:
        return tokens[i], i + 1
    except IndexError:
        return Token(Tok.EMPTY, ""), i + 1


def tail(tokens: list[Token], i: int) -> list[Token]:
    try:
        return tokens[i:]
    except IndexError:
        return []


