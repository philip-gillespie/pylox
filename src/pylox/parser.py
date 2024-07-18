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

    def parse(self) -> list[stmt.Stmt]:
        """Parse the tokens into a list of statements."""
        statements = list()
        while not self.is_at_end():
            statement: stmt.Stmt | None = self.declaration()
            statements.append(statement)
        return statements

    def is_at_end(self):
        """Check if current token is EOF (End Of File)."""
        current_token = self.tokens[self.current]
        return current_token.token_type == TokenType.EOF

    def declaration(self):
        """Checks for Variable declaration, otherwise runs as a statement."""
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParserError:
            self.synchronise()
            return None

    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        """Checks whether the current token matches the token_type."""
        # if self.is_at_end():
        #     return False
        current_token: Token = self.tokens[self.current]
        return current_token.token_type == token_type

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
        return self.assignment()

    def assignment(self) -> expr.Expr:
        expression = self._or()
        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: expr.Expr = self.assignment()
            if isinstance(expression, expr.Variable):
                name: Token = expression.name
                return expr.Assign(name, value)
            raise ParserError(equals, "Invalid assignment target")
            # Book says do not throw error.
            # Book uses function `error`
        return expression

    def _or(self) -> expr.Expr:
        """Handle Or Expression or pass through."""
        expression: expr.Expr = self._and()
        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: expr.Expr = self._and()
            expression = expr.Logical(expression, operator, right)
        return expression

    def _and(self)-> expr.Expr:
        "Handle And Expression or pass through."
        expression: expr.Expr = self.equality()
        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: expr.Expr = self.equality()
            expression = expr.Logical(expression, operator, right)
        return expression
        

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
        """Return the next statement from the tokens."""
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return stmt.BlockStmt(self.block())
        return self.expression_statement()

    def if_statement(self):
        """Parse an if statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect `(` after `if`.")
        condition: expr.Expr = self.expression();
        self.consume(TokenType.RIGHT_PAREN, "Expect `)` after condition.")
        then_branch: stmt.Stmt = self.statement()
        else_branch: stmt.Stmt| None = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return stmt.IfStmt(condition, then_branch, else_branch)

    def while_statement(self) -> stmt.Stmt:
        """Parse a while statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect `(` after `while`.")
        condition: expr.Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect `)` after condition.")
        body: stmt.Stmt = self.statement()
        return stmt.WhileStmt(condition, body)

    def block(self) -> list[stmt.Stmt]:
        statements = list()
        while (not self.check(TokenType.RIGHT_BRACE)) and (not self.is_at_end()):
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect `}` after block.")
        return statements

    def print_statement(self) -> stmt.Stmt:
        value: expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect `;` after value")
        return stmt.PrintStmt(value)

    def expression_statement(self) -> stmt.Stmt:
        expression: expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect `;` after value")
        return stmt.ExpressionStmt(expression)
