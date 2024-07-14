from typing import Any

from pylox.runtime_error import RuntimeError
from pylox.tokens import Token


class Environment:
    def __init__(self) -> None:
        self.values: dict[str, Any] = dict()

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        try:
            return self.values[name.lexeme]
        except KeyError:
            raise RuntimeError(name, f"Undefined variable `{name.lexeme}`.")
