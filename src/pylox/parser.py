"""parser.py"""

from pylox.tokens import TokenType, Token

# from pylox.expr import Expr, Binary, Unary, Literal, Grouping
from pylox import stmt
from pylox import expr


class ParserError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def is_at_end(self):
        return self.peek().token_type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self) -> Token:
        """Return the most recently consumed token."""
        return self.tokens[self.current - 1]

    def expression(self) -> expr.Expr:
        return self.equality()

    def equality(self) -> expr.Expr:
        expression: expr.Expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: expr.Expr = self.comparison()
            expression = expr.Binary(expression, operator, right)
        return expression

    def comparison(self) -> expr.Expr:
        expression: expr.Expr = self.term()
        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator: Token = self.previous()
            right: expr.Expr = self.term()
            expression = expr.Binary(expression, operator, right)
        return expression

    def term(self) -> expr.Expr:
        expression: expr.Expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: expr.Expr = self.factor()
            expression = expr.Binary(expression, operator, right)
        return expression

    def factor(self) -> expr.Expr:
        expression: expr.Expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: expr.Expr = self.unary()
            expression = expr.Binary(expression, operator, right)
        return expression

    def unary(self) -> expr.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: expr.Expr = self.unary()
            return expr.Unary(operator, right)
        return self.primary()

    def primary(self) -> expr.Expr:
        if self.match(TokenType.FALSE):
            return expr.Literal(False)
        if self.match(TokenType.TRUE):
            return expr.Literal(True)
        if self.match(TokenType.NIL):
            return expr.Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return expr.Literal(self.previous().literal)
        if self.match(TokenType.IDENTIFIER):
            return expr.Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expression = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr.Grouping(expression)
        raise ParserError(self.peek(), "Expext Expression")

    def consume(self, token_type: TokenType, message: str):
        if self.check(token_type):
            return self.advance()
        raise ParserError(self.peek(), message)

    def synchronise(self):
        self.advance()
        # most statements start with one of these
        statement_starts = [
            TokenType.CLASS,
            TokenType.FUN,
            TokenType.VAR,
            TokenType.FOR,
            TokenType.IF,
            TokenType.WHILE,
            TokenType.PRINT,
            TokenType.RETURN,
        ]
        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return None
            if self.peek().token_type in statement_starts:
                return None
            self.advance()

    # def parse(self) -> Expr | None:
    #     try:
    #         return self.expression()
    #     except ParserError:
    #         return None

    def parse(self) -> list[stmt.Stmt]:
        statements = list()
        while not self.is_at_end():
            statement: stmt.Stmt | None = self.declaration()
            statements.append(statement)
        return statements

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParserError:
            self.synchronise()
            return None

    def var_declaration(self) -> stmt.Stmt:
        name: Token = self.consume(
            TokenType.IDENTIFIER,
            "Expect variable name.",
        )
        initialiser: expr.Expr | None = None
        if self.match(TokenType.EQUAL):
            initialiser = self.expression()
        self.consume(
            TokenType.SEMICOLON,
            "Expect `;` after variable declaration",
        )
        return stmt.VarStmt(name, initialiser)

    def statement(self) -> stmt.Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()

    def print_statement(self) -> stmt.Stmt:
        value: expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect `;` after value")
        return stmt.PrintStmt(value)

    def expression_statement(self) -> stmt.Stmt:
        expression: expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect `;` after value")
        return stmt.ExpressionStmt(expression)
