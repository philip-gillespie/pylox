# from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Protocol

from pylox.expr import Expr
from pylox.tokens import Token


# class Stmt(ABC):
#     pass

class Stmt(Protocol): pass

@dataclass
class Block():
    statements: list[Stmt]


@dataclass
class Expression():
    expression: Expr


@dataclass
class FunctionStmt(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None


@dataclass
class PrintStmt():
    expression: Expr


@dataclass
class ReturnStmt(Stmt):
    keyword: Token
    value: Expr | None


@dataclass
class Var(Stmt):
    name: Token
    initialiser: Expr | None


@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt
