from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from pylox.expr import Expr
from pylox.tokens import Token

class Stmt(ABC):

	@abstractmethod
	def accept(self, visitor: StmtVisitor) -> Any:
		pass


class StmtVisitor(ABC):

	@abstractmethod
	def visit_block_stmt(self, block_stmt: BlockStmt) -> Any:
		pass

	@abstractmethod
	def visit_expression_stmt(self, expression_stmt: ExpressionStmt) -> Any:
		pass

	@abstractmethod
	def visit_print_stmt(self, print_stmt: PrintStmt) -> Any:
		pass

	@abstractmethod
	def visit_var_stmt(self, var_stmt: VarStmt) -> Any:
		pass


class BlockStmt(Stmt):

	def __init__(self, statements: list[Stmt]):
		self.statements = statements

	def accept(self, visitor: StmtVisitor)-> Any:
		return visitor.visit_block_stmt(self)

class ExpressionStmt(Stmt):

	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: StmtVisitor)-> Any:
		return visitor.visit_expression_stmt(self)

class PrintStmt(Stmt):

	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: StmtVisitor)-> Any:
		return visitor.visit_print_stmt(self)

class VarStmt(Stmt):

	def __init__(self, name: Token, initialiser: Expr | None):
		self.name = name
		self.initialiser = initialiser

	def accept(self, visitor: StmtVisitor)-> Any:
		return visitor.visit_var_stmt(self)