from __future__ import annotations

from pylox.runtime_error import RuntimeError
from pylox.tokens import Token


class Environment:
    def __init__(
        self,
        values: dict[str, object] | None = None,
        enclosing: Environment | None = None,
        globals: Environment | None = None,
    ) -> None:
        self.enclosing: Environment | None = enclosing
        if values is None:
            self.values = dict()
        else:
            self.values = values
        if globals == None:
            self.globals = self
        else:
            self.globals = globals

    def __repr__(self) -> str:
        return f"Environment(values={self.values}),enclosing=({self.enclosing}))"

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, Environment):
            return False
        if (self.values == other.values) and (self.enclosing == other.enclosing):
            return True
        return False

    def define(self, name: str, value: object) -> Environment:
        return self.get_copy_with(name, value)

    def copy(self):
        output_values = self.values.copy()
        return Environment(
            values=output_values,
            enclosing=self.enclosing,
            globals=self.globals,
        )

    def get_copy_with(self, key: str, value: object) -> Environment:
        output_values = self.values.copy()
        output_values[key] = value
        return Environment(
            values=output_values,
            enclosing=self.enclosing,
            globals=self.globals,
        )

    def get(self, name: Token) -> object:
        value = self.values.get(name.lexeme)
        if (value is None) and (self.enclosing is not None):
            value = self.enclosing.get(name)
        if value is None:
            raise RuntimeError(name, f"Undefined variable `{name.lexeme}`.")
        return value

    def assign(self, name: Token, value: object) -> Environment:
        if name.lexeme in self.values:
            return self.get_copy_with(name.lexeme, value)
        if self.enclosing is not None:
            output = Environment(
                values=self.values, enclosing=self.enclosing.assign(name, value)
            )
            return output
        raise RuntimeError(name, f"Undefined variable `{name.lexeme}`.")
