import argparse
import re


def main():
    parser = argparse.ArgumentParser(prog="generate_ast")
    parser.add_argument("output_dir", nargs=1)
    args = parser.parse_args()
    output_dir = args.output_dir[0]
    define_ast(
        output_dir,
        "expr",
        [
            "Assign = name: Token, value: Expr",
            "Binary = left: Expr, operator: Token, right: Expr",
            "Call = callee: Expr, paren: Token, arguments: list[Expr]",
            "Grouping = expression: Expr",
            "Literal = value: Any",
            "Logical = left: Expr, operator: Token, right: Expr",
            "Unary = operator: Token, right: Expr",
            "Variable = name: Token",
        ],
        "from pylox.scanner import Token\n",
    )
    define_ast(
        output_dir,
        "stmt",
        [
            "BlockStmt = statements: list[Stmt]",
            "ExpressionStmt = expression: Expr",
            "FunctionStmt = name: Token, params: list[Token], body: list[Stmt]",
            "IfStmt = condition: Expr, then_branch: Stmt, else_branch: Stmt | None",
            "PrintStmt = expression: Expr",
            "VarStmt = name: Token, initialiser: Expr | None",
            "WhileStmt = condition: Expr, body: Stmt",
        ],
        "from pylox.expr import Expr\nfrom pylox.tokens import Token",
    )


def define_ast(
    output_dir: str,
    base_name: str,
    types: list[str],
    extra_imports: str,
):
    path = f"{output_dir}/{base_name}.py"
    abc_name = "".join(base_name.title().split("_"))  # snake to pascal case
    output_text = [
        "from __future__ import annotations\n",
        "from abc import ABC, abstractmethod\n",
        "from typing import Any\n",
        "\n",
        extra_imports,
        "\n",
        "\n",
        f"class {abc_name}(ABC):\n",
        "\n",
        "\t@abstractmethod\n",
        f"\tdef accept(self, visitor: {abc_name}Visitor) -> Any:\n",
        "\t\tpass\n",
    ]

    visitor_lines = define_visitor(abc_name, types)
    output_text.extend(visitor_lines)
    subclass_lines = define_subclasses(abc_name, types)
    output_text.extend(subclass_lines)

    with open(path, "w") as f:
        f.writelines(output_text)


def define_subclasses(abc_name: str, token_types: list[str]) -> list[str]:
    output_text = []
    for token in token_types:
        class_name = token.split("=")[0].strip()
        fields = token.split("=")[1].strip()
        class_text = define_subclass(abc_name, class_name, fields)
        output_text.extend(class_text)
    return output_text


def define_subclass(abc_name: str, class_name: str, fields: str) -> list[str]:
    output_text = [
        "\n\n",
        f"class {class_name}({abc_name}):\n",
        "\n",
        f"\tdef __init__(self, {fields}):\n",
    ]
    for field in fields.split(", "):
        field_name = field.split(": ")[0]
        output_text.extend([f"\t\tself.{field_name} = {field_name}\n"])

    snake_name = pascal_to_snake(class_name)
    accept_lines = [
        "\n",
        f"\tdef accept(self, visitor: {abc_name}Visitor)-> Any:\n",
        f"\t\treturn visitor.visit_{snake_name}(self)",
    ]
    output_text.extend(accept_lines)
    return output_text


def define_visitor(abc_name: str, types: list[str]) -> list[str]:
    output_text = [
        "\n\n",
        f"class {abc_name}Visitor(ABC):\n",
    ]
    for token in types:
        class_name = token.split("=")[0].strip()
        snake_name = pascal_to_snake(class_name)
        new_lines = [
            "\n",
            "\t@abstractmethod\n",
            f"\tdef visit_{snake_name}(self, {snake_name}: {class_name}) -> Any:\n",
            "\t\tpass\n",
        ]
        output_text.extend(new_lines)
    return output_text


def pascal_to_snake(text: str) -> str:
    """Convert a string in pasacl case to a string in snake case."""
    pattern = re.compile(r"(?<!^)(?=[A-Z]+)")
    spaced = pattern.sub("_", text)  # Pascal_Case
    output = spaced.lower()  # pascal_case
    return output


if __name__ == "__main__":
    main()
