from typing import Protocol, runtime_checkable
from abc import ABC, abstractmethod 
from pylox.environment import Environment

class LoxCallable(ABC):

    @abstractmethod
    def call(
        self, arguments: list[object], env: Environment
    ) -> tuple[object, Environment]: ...

    @abstractmethod
    def arity(self) -> int: ...
