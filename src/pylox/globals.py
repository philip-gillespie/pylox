import time

from pylox.environment import Environment
from pylox.lox_callable import LoxCallable


class Clock(LoxCallable):
    """Inbuilt clock"""

    def call(
        self,
        arguments: list,
        env: Environment,
    ) -> tuple[float, Environment]:
        return time.time(), env

    def arity(self):
        return 0
