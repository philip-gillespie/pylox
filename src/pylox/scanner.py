from pylox.tokens import Token, TokenType


KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


class ScannerError(Exception):
    def __init__(self, line, message):
        self.line = line
        self.message = message

class Scanner:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        end_token = Token(TokenType.EOF, "", None, self.line)
        self.tokens.append(end_token)

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self) -> None:
        char: str = self.advance()
        match char:
            # single character tokens
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "!":
                token_type = TokenType.BANG
                if self.peek() == "=":
                    self.current += 1
                    token_type = TokenType.BANG_EQUAL
                self.add_token(token_type)
            case "=":
                token_type = TokenType.EQUAL
                if self.peek() == "=":
                    self.current += 1
                    token_type = TokenType.EQUAL_EQUAL
                self.add_token(token_type)
            case "<":
                token_type = TokenType.LESS
                if self.peek() == "=":
                    self.current += 1
                    token_type = TokenType.LESS_EQUAL
                self.add_token(token_type)
            case ">":
                token_type = TokenType.GREATER
                if self.peek() == "=":
                    self.current += 1
                    token_type = TokenType.GREATER_EQUAL
                self.add_token(token_type)
            # Comments
            case "/":
                if self.peek() == "/":
                    while (self.peek() != "\n") and (not self.is_at_end()):
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            # Increment on newline
            case "\n":
                self.line += 1
            # Whitespace - ignore
            case c if c.isspace():
                pass
            # Strings
            case '"':
                self.string()
            # Digits
            case c if c.isdigit():
                self.number()
            # Identifier
            case c if c.isidentifier():  # A-Z,a-z,_
                self.identifier()
            # Unexpected character
            case _:
                raise ScannerError(self.line, f"Unexpected Character: {char}")
                # self.lox.error(self.line, f"Unexpected Character: {char}")
        return None

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def add_token(self, token_type: TokenType, literal=None):
        lexeme: str = self.source[self.start : self.current]
        token = Token(token_type, lexeme, literal, self.line)
        self.tokens.append(token)

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def string(self):
        while (self.peek() != '"') and (not self.is_at_end()):
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            raise ScannerError(self.line, "unterminated string")
            # self.lox.error(self.line, "unterminated string")

        # advance beyond closing "
        self.advance()
        # Trim the quotation marks
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()
        if (self.peek() == ".") and (self.peak_next()):
            self.advance()
            while self.peek().isdigit():
                self.advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def peak_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def identifier(self):
        is_identifier = self.peek().isidentifier() or self.peek().isalnum()
        while is_identifier:
            self.advance()
            is_identifier = self.peek().isidentifier() or self.peek().isalnum()
        text: str = self.source[self.start : self.current]
        token_type: TokenType | None = KEYWORDS.get(text)
        if token_type is None:
            token_type = TokenType.IDENTIFIER
        self.add_token(token_type)
