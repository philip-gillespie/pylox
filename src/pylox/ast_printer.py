from typing import Any
from pylox import expr, stmt
from pylox.scanner import Token, TokenType


def main():
    expression = expr.Binary(
        left=expr.Unary(
            operator=Token(TokenType.MINUS, "-", None, 1),
            right=expr.Literal(123),
        ),
        operator=Token(TokenType.STAR, "*", None, 1),
        right=expr.Grouping(
            expression=expr.Binary(
                left=expr.Literal(12),
                operator=Token(TokenType.SLASH, "/", None, 1),
                right=expr.Literal(6),
            )
        ),
    )
    output: str = AstPrinter().print(expression)
    print(output)


class AstPrinter(expr.ExprVisitor, stmt.StmtVisitor):
    def print(self, text: expr.Expr| stmt.Stmt) -> str:
        return text.accept(self)  # calls one of the visit methods

    def visit_var_stmt(self, var_stmt: stmt.VarStmt) -> Any:
        return self.parenthesize("define", var_stmt.initialiser)

    def visit_variable(self, variable: expr.Variable) -> Any:
        return self.parenthesize("access", variable)

    def visit_print_stmt(self, print_stmt: stmt.PrintStmt) -> Any:
        return self.parenthesize("print", print_stmt.expression)

    def visit_expression_stmt(self, expression_stmt: stmt.ExpressionStmt) -> Any:
        return self.parenthesize("", expression_stmt.expression)

    def visit_binary(self, binary: expr.Binary) -> str:
        return self.parenthesize(
            binary.operator.lexeme,
            binary.left,
            binary.right,
        )

    def visit_grouping(self, grouping: expr.Grouping) -> str:
        return self.parenthesize("group", grouping.expression)

    def visit_literal(self, literal: expr.Literal) -> str:
        if literal.value == None:
            return "nil"
        if isinstance(literal.value, str):
            return f'"{literal.value}"'
        return str(literal.value)

    def visit_unary(self, unary: expr.Unary) -> str:
        return self.parenthesize(unary.operator.lexeme, unary.right)

    def parenthesize(self, name: str, *args: expr.Expr | None) -> str:
        output_words = [f"({name}"]
        for expression in args:
            if expression is None:
                output_words.append("`None`")
                continue
            nested: str = expression.accept(self)
            output_words.append(f" {nested}")
        output_words.append(")")
        return "".join(output_words)


if __name__ == "__main__":
    main()
