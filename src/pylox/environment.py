from typing import Any

from pylox.runtime_error import RuntimeError
from pylox.tokens import Token


class Environment:
    def __init__(self, enclosing=None) -> None:
        self.enclosing: Environment | None = enclosing
        self.values: dict[str, Any] = dict()

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        value = self.values.get(name.lexeme)
        if (value is None) and (self.enclosing is not None):
            value = self.enclosing.get(name)
        if value is None:
            raise RuntimeError(name, f"Undefined variable `{name.lexeme}`.")
        return value

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return None
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return None
        raise RuntimeError(name, f"Undefined variable `{name.lexeme}`.")
