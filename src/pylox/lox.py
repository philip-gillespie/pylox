from pylox import stmt
from pylox.interpreter import Interpreter
from pylox.scanner import Scanner, ScannerError
from pylox.tokens import Token, TokenType
from pylox.parser import Parser, ParserError
from pylox.ast_printer import AstPrinter
from pylox.runtime_error import RuntimeError


class Lox:
    def __init__(self) -> None:
        self.had_runtime_error = False

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

    def run(self, content: str):
        scanner = Scanner(source=content)
        try:
            scanner.scan_tokens()
        except ScannerError as e:
            self.error(e.line, e.message)
            return None
        tokens: list[Token] = scanner.tokens
        # print(tokens)
        parser = Parser(tokens)
        try:
            statements: list[stmt.Stmt] = parser.parse()
        except ParserError as e:
            if e.token.token_type == TokenType.EOF:
                self.report(e.token.line, " at end ", e.message)
            else:
                self.report(e.token.line, f" at '{e.token.lexeme}' ", e.message)
            return None
        # printer = AstPrinter()
        # for statement in statements:
        #     print(printer.print(statement))
        interpreter = Interpreter()
        try:
            interpreter.interpret(statements)
        except RuntimeError as e:
            print(f"{e.message}\n[line {e.token.line}]")
            self.had_runtime_error = True
        return None

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}:{message}")


