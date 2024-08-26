from typing import Sequence, Protocol, runtime_checkable


from pylox import stmt, expr
from pylox.tokens import Token, Tok
from pylox.environment import Environment
from pylox.lox_callable import LoxCallable


class RuntimeError(Exception):
    """
    Error that arises from the interpreter.
    """

    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.token = token


ERROR_FLOAT_OPERANDS = "Operands must be numbers."


def interpret(statements: Sequence[stmt.Stmt], env: Environment) -> Environment:
    return interpret_statements(statements, env)


def interpret_statements(
    statements: Sequence[stmt.Stmt], env: Environment
) -> Environment:
    """Interpret a sequence of statements, return the resulting environment."""
    for statement in statements:
        env = interpret_statement(statement, env)
    return env


def interpret_statement(statement: stmt.Stmt, env: Environment) -> Environment:
    """Interpret a single statement, return the resulting environment."""
    if isinstance(statement, stmt.PrintStmt):
        result, new_env = evaluate(statement.expression, env)
        print(stringify(result))
        return new_env
    if isinstance(statement, stmt.Expression):
        _, new_env = evaluate(statement.expression, env)
        return new_env
    if isinstance(statement, stmt.Var):
        env = interpret_var_statement(statement, env)
        return env
    if isinstance(statement, stmt.Block):
        env = interpret_block_statement(statement, env)
        return env
    if isinstance(statement, stmt.IfStmt):
        return interpret_if_statement(statement, env)
    if isinstance(statement, stmt.While):
        return interpret_while_statement(statement, env)
    else:
        raise NotImplementedError("not yet implemented")


def interpret_if_statement(statement: stmt.IfStmt, env: Environment) -> Environment:
    value, condition_env = evaluate(statement.condition, env)
    if is_truthy(value):
        return interpret_statement(statement.then_branch, condition_env)
    if statement.else_branch is not None:
        return interpret_statement(statement.else_branch, condition_env)
    return condition_env


def interpret_while_statement(statement: stmt.While, env: Environment) -> Environment:
    condition, while_env = evaluate(statement.condition, env)
    while is_truthy(condition):
        while_env = interpret_statement(statement.body, while_env)
        condition, while_env = evaluate(statement.condition, while_env)
    return while_env


def interpret_block_statement(
    statement: stmt.Block,
    env: Environment,
) -> Environment:
    """Interpret a block statement
    Return the resulting environment
    """
    inner_statements = statement.statements
    inner_env = Environment(enclosing=env)
    inner_env = interpret_statements(inner_statements, inner_env)
    updated_env: Environment | None = inner_env.enclosing
    assert updated_env is not None
    return updated_env


def interpret_var_statement(statement: stmt.Var, env: Environment) -> Environment:
    """
    Interpret a variable declaration statement.
    Return the resulting environment.
    """
    if statement.initialiser == None:
        return env.define(statement.name.lexeme, None)
    value, new_env = evaluate(statement.initialiser, env)
    return new_env.define(statement.name.lexeme, value)


def stringify(item: object) -> str:
    """Return a string representation of an object."""
    if isinstance(item, bool) and item == True:
        return "true"
    if isinstance(item, bool) and item == False:
        return "false"
    if item == None:
        return "nil"
    return str(item)


def evaluate(
    expression: expr.Expr,
    env: Environment,
) -> tuple[object, Environment]:
    """
    Evaluate an expression.
    Return the resulting value and environment.
    """
    if isinstance(expression, expr.Literal):
        return evaluate_literal(expression, env)
    if isinstance(expression, expr.Grouping):
        return evaluate_grouping(expression, env)
    if isinstance(expression, expr.Unary):
        return evaluate_unary(expression, env)
    if isinstance(expression, expr.Binary):
        return evaluate_binary(expression, env)
    if isinstance(expression, expr.Variable):
        return evaluate_variable(expression, env)
    if isinstance(expression, expr.Assign):
        return evaluate_assign(expression, env)
    if isinstance(expression, expr.Logical):
        return evaluate_logical(expression, env)
    if isinstance(expression, expr.Call):
        return evaluate_call(expression, env)
    raise NotImplementedError(f"{expression}")


def evaluate_call(
    expression: expr.Call, env: Environment
) -> tuple[object, Environment]:
    callee, new_env = evaluate(expression.callee, env)
    if not isinstance(callee, LoxCallable):
        raise RuntimeError(
            expression.paren,
            "Can only call functions and classes",
        )
    if len(expression.arguments) != callee.arity():
        raise RuntimeError(
            expression.paren,
            f"Expected {callee.arity()} arguments but received {len(expression.arguments)}.",
        )
    arguments: list[object] = list()
    for arg_expr in expression.arguments:
        arg, new_env = evaluate(arg_expr, new_env)
        arguments.append(arg)
    return callee.call(arguments, new_env)


def evaluate_logical(
    expression: expr.Logical, env: Environment
) -> tuple[object, Environment]:
    """
    Evaluate a logical expression.
    Return the result, and the resulting environment.
    """
    if expression.operator.token_type == Tok.OR:
        return evaluate_logical_or(expression, env)
    if expression.operator.token_type == Tok.AND:
        return evaluate_logical_and(expression, env)
    raise RuntimeError(expression.operator, "Unrecognised logical operator.")


def evaluate_logical_or(
    expression: expr.Logical, env: Environment
) -> tuple[object, Environment]:
    """
    Evaluate a logical "or" expression.
    Return the result, and the resulting environment.
    """
    left_value, left_env = evaluate(expression.left, env)
    if is_truthy(left_value):
        return left_value, left_env
    right_value, right_env = evaluate(expression.right, left_env)
    return right_value, right_env


def evaluate_logical_and(
    expression: expr.Logical, env: Environment
) -> tuple[object, Environment]:
    """
    Evaluate a logical "and" expression.
    Return the result, and the resulting environment.
    """
    left_value, left_env = evaluate(expression.left, env)
    if not is_truthy(left_value):
        return left_value, left_env
    # left_value is truthy
    right_value, right_env = evaluate(expression.right, left_env)
    return right_value, right_env


def evaluate_assign(
    expression: expr.Assign, env: Environment
) -> tuple[object, Environment]:
    """
    Interpret and assignemnt expression.
    Return None, and the resulting environment.
    """
    value, new_env = evaluate(expression.value, env)
    key = expression.name
    output_env = new_env.assign(key, value)
    return None, output_env


def evaluate_variable(
    expression: expr.Variable, env: Environment
) -> tuple[object, Environment]:
    """
    Interpret an expression referencing a variable in the environment.
    Return the value and the environment.
    """
    result = env.get(expression.name)
    return result, env


def evaluate_literal(
    expression: expr.Literal, env: Environment
) -> tuple[object, Environment]:
    """
    Return the literal value from the expression, and the resulting environment.
    """
    return expression.value, env


def evaluate_grouping(
    expression: expr.Grouping, env: Environment
) -> tuple[object, Environment]:
    """
    Interpret a grouping expression.
    Return the evaluated inner value and environment.
    """
    internal: expr.Expr = expression.expression
    return evaluate(internal, env)


def evaluate_unary(
    expression: expr.Unary, env: Environment
) -> tuple[object, Environment]:
    """
    Interpret a unary expression.
    Return the resulting value and environment.
    """
    right, output_env = evaluate(expression.right, env)
    operator: Token = expression.operator
    match operator.token_type:
        case Tok.MINUS:
            if isinstance(right, float):
                return -right, output_env
            raise RuntimeError(operator, "Operand must be a number.")
        case Tok.BANG:
            truthy: bool = is_truthy(right)
            return not (truthy), output_env
        case _:
            raise RuntimeError(operator, "Invalid operator.")


def is_truthy(value: object) -> bool:
    """
    Is the object truthy according to lox?
    Return the boolean answer.
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return True


BINARY_NUMERIC_OPERATIONS = {
    Tok.GREATER: lambda left, right: left > right,
    Tok.GREATER_EQUAL: lambda left, right: left >= right,
    Tok.LESS: lambda left, right: left < right,
    Tok.LESS_EQUAL: lambda left, right: left <= right,
    Tok.MINUS: lambda left, right: left - right,
    Tok.SLASH: lambda left, right: left / right,
    Tok.STAR: lambda left, right: left * right,
}


def evaluate_binary(
    expression: expr.Binary, env: Environment
) -> tuple[object, Environment]:
    """
    Interpret a binary expression.
    Return the resulting value and environment.
    """
    left, new_env = evaluate(expression.left, env)
    right, output_env = evaluate(expression.right, new_env)
    operator: Token = expression.operator
    match operator.token_type:
        case t if t in BINARY_NUMERIC_OPERATIONS:
            # left and right are only allowed to be numeric
            return evaluate_binary_numeric(left, operator, right), output_env
        case Tok.PLUS:
            return add(left, operator, right), output_env
        case Tok.BANG_EQUAL:
            return not is_equal(left, right), output_env
        case Tok.EQUAL_EQUAL:
            return is_equal(left, right), output_env
        case _:
            raise RuntimeError(operator, "Unexpected operator.")


def evaluate_binary_numeric(left: object, operator: Token, right: object):
    operation = BINARY_NUMERIC_OPERATIONS[operator.token_type]
    if not isinstance(left, float) or not isinstance(right, float):
        raise RuntimeError(operator, ERROR_FLOAT_OPERANDS)
    return operation(left, right)


def add(left: object, operator: Token, right: object) -> object:
    if isinstance(left, float) and isinstance(right, float):
        return left + right
    if isinstance(left, str) and isinstance(right, str):
        return left + right
    raise RuntimeError(
        operator,
        "Operands must be two numbers or two strings",
    )


def is_equal(left: object, right: object) -> bool:
    if left is None and right is None:
        return True
    if left is None:
        return False
    return left == right
