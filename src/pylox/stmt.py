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
	def visit_if_stmt(self, if_stmt: IfStmt) -> Any:
		pass

	@abstractmethod
	def visit_print_stmt(self, print_stmt: PrintStmt) -> Any:
		pass

	@abstractmethod
	def visit_var_stmt(self, var_stmt: VarStmt) -> Any:
		pass

	@abstractmethod
	def visit_while_stmt(self, while_stmt: WhileStmt) -> Any:
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

class IfStmt(Stmt):

	def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None):
		self.condition = condition
		self.then_branch = then_branch
		self.else_branch = else_branch

	def accept(self, visitor: StmtVisitor)-> Any:
		return visitor.visit_if_stmt(self)

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

class WhileStmt(Stmt):

	def __init__(self, condition: Expr, body: Stmt):
		self.condition = condition
		self.body = body

	def accept(self, visitor: StmtVisitor)-> Any:
		return visitor.visit_while_stmt(self)