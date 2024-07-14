from typing import Any
from pylox import expr
from pylox import stmt
from pylox.runtime_error import RuntimeError
from pylox.tokens import Token, TokenType
from pylox.environment import Environment


class Interpreter(expr.ExprVisitor, stmt.StmtVisitor):
    def __init__(self) -> None:
        self.environment = Environment()

    def visit_var_stmt(self, var_stmt: stmt.VarStmt) -> Any:
        value: Any = None
        if var_stmt.initialiser != None:
            value = self.evaluate(var_stmt.initialiser)
        self.environment.define(var_stmt.name.lexeme, value)
        return None

    def visit_assign(self, assign: expr.Assign) -> Any:
        value: Any = self.evaluate(assign.value)
        self.environment.assign(assign.name, value)
        return value

    def visit_variable(self, variable: expr.Variable) -> Any:
        return self.environment.get(variable.name)

    def visit_expression_stmt(self, expression_stmt: stmt.ExpressionStmt) -> Any:
        self.evaluate(expression_stmt.expression)
        return None

    def visit_print_stmt(self, print_stmt: stmt.PrintStmt) -> Any:
        value: Any = self.evaluate(print_stmt.expression)
        print(value)
        return None

    def evaluate(self, expression: expr.Expr) -> Any:
        return expression.accept(self)

    def visit_literal(self, literal: expr.Literal) -> Any:
        return literal.value

    def visit_grouping(self, grouping: expr.Grouping) -> Any:
        return self.evaluate(grouping.expression)

    def visit_unary(self, unary: expr.Unary) -> Any:
        right = self.evaluate(unary.right)
        match unary.operator.token_type:
            case TokenType.MINUS:
                self.check_number_operand(unary.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not self.is_truthy(right)
        raise NotImplementedError(
            "need to implement error handling for the interpreter"
        )

    def is_truthy(self, value: Any) -> bool:
        """False and `nil` are Falsey, everything else is Truthy"""
        match value:
            case None:
                return False
            case bool():
                return value
            case _:
                return True

    def visit_binary(self, binary: expr.Binary) -> Any:
        left: Any = self.evaluate(binary.left)
        right: Any = self.evaluate(binary.right)
        match binary.operator.token_type:
            case TokenType.GREATER:
                self.check_number_operands(binary.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(binary.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.check_number_operands(binary.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(binary.operator, left, right)
                return float(left) <= float(right)
            case TokenType.MINUS:
                self.check_number_operands(binary.operator, left, right)
                return float(left) - float(right)
            case TokenType.SLASH:
                self.check_number_operands(binary.operator, left, right)
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(binary.operator, left, right)
                return float(left) * float(right)
            case TokenType.PLUS:
                # acting as if this is a statically typed language
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                raise RuntimeError(
                    binary.operator,
                    "Operands must be two numbers or two strings",
                )
            case TokenType.BANG_EQUAL:
                return not left == right
            case TokenType.EQUAL_EQUAL:
                return left == right
        raise NotImplementedError()

    def check_number_operand(self, operator: Token, operand: Any):
        if isinstance(operand, float):
            return None
        raise RuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: Any, right: Any):
        if isinstance(left, float) and isinstance(right, float):
            return None
        raise RuntimeError(operator, "Operands must be numbers.")

    # def interpret(self, expression: expr.Expr) -> None:
    #     value = self.evaluate(expression)
    #     print(str(value))

    def interpret(self, statements: list[stmt.Stmt]) -> None:
        for statement in statements:
            self.execute(statement)

    def execute(self, statement: stmt.Stmt):
        statement.accept(self)


if __name__ == "__main__":
    interpreter = Interpreter()
