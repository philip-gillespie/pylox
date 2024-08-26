from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass

from pylox.scanner import Token


class Expr(Protocol): pass

@dataclass
class Assign():
    name: Token
    value: Expr


@dataclass
class Binary():
    left: Expr
    operator: Token
    right: Expr


@dataclass
class Call():
    callee: Expr
    paren: Token
    arguments: list[Expr]

@dataclass
class Empty(): pass

@dataclass
class Grouping():
    expression: Expr


@dataclass
class Literal():
    value: object


@dataclass
class Logical():
    left: Expr
    operator: Token
    right: Expr


@dataclass
class Unary():
    operator: Token
    right: Expr

@dataclass
class Variable():
    name: Token

