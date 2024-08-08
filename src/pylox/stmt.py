# from __future__ import annotations
from abc import ABC
from dataclasses import dataclass

from pylox.expr import Expr
from pylox.tokens import Token


class Stmt(ABC):
    pass


@dataclass
class BlockStmt(Stmt):
    statements: list[Stmt]


@dataclass
class ExpressionStmt(Stmt):
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
class PrintStmt(Stmt):
    expression: Expr


@dataclass
class ReturnStmt(Stmt):
    keyword: Token
    value: Expr | None


@dataclass
class VarStmt(Stmt):
    name: Token
    initialiser: Expr | None


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt
