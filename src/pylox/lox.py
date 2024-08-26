from typing import Sequence
from pylox.environment import Environment
from pylox.stmt import Stmt
from pylox.tokens import Token, Tok

from pylox import interpreter, scanner, parser, globals


environment = Environment(values={"clock": globals.Clock()})

class Lox:
    def __init__(self) -> None:
        self.had_runtime_error = False
        self.env = environment

    def run_file(self, filename: str):
        with open(filename, encoding="utf-8") as f:
            content = f.read()
        self.run(content)

    def run_prompt(self):
        while True:
            try:
                content = input("> ")
            except EOFError:
                break
            self.run(content)

    def run(self, code: str):
        tokens: list[Token] = scanner.scan(code)
        try:
            tokens: list[Token] = scanner.scan(code)
        except scanner.ScannerError as e:
            self.error(e.line, e.message)
            return None
        try:
            statements: Sequence[Stmt] = parser.parse(tokens)
        except parser.ParserError as e:
            if e.token is not None:
                line = e.token.line
            else:
                line = 0
            self.error(line, e.message)
            self.run_prompt()
        else:
            self.env = interpreter.interpret_statements(statements, self.env)


    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}:{message}")

