from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass

from pylox.scanner import Token

# @dataclass
# class Expr(ABC): ...

class Expr(Protocol):
    length: int

@dataclass
class Assign():
    name: Token
    value: Expr


@dataclass
class Binary():
    left: Expr
    operator: Token
    right: Expr
    length: int


@dataclass
class Call():
    callee: Expr
    paren: Token
    arguments: list[Expr]

@dataclass
class Empty():
    length=0

@dataclass
class Grouping():
    expression: Expr
    length: int 


@dataclass
class Literal():
    value: object
    length: int


@dataclass
class Logical():
    left: Expr
    operator: Token
    right: Expr


@dataclass
class Unary():
    operator: Token
    right: Expr
    length: int

@dataclass
class Variable():
    name: Token

