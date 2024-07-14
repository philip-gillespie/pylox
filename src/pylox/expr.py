from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from pylox.scanner import Token


class Expr(ABC):

	@abstractmethod
	def accept(self, visitor: ExprVisitor) -> Any:
		pass


class ExprVisitor(ABC):

	@abstractmethod
	def visit_assign(self, assign: Assign) -> Any:
		pass

	@abstractmethod
	def visit_binary(self, binary: Binary) -> Any:
		pass

	@abstractmethod
	def visit_grouping(self, grouping: Grouping) -> Any:
		pass

	@abstractmethod
	def visit_literal(self, literal: Literal) -> Any:
		pass

	@abstractmethod
	def visit_unary(self, unary: Unary) -> Any:
		pass

	@abstractmethod
	def visit_variable(self, variable: Variable) -> Any:
		pass


class Assign(Expr):

	def __init__(self, name: Token, value: Expr):
		self.name = name
		self.value = value

	def accept(self, visitor: ExprVisitor)-> Any:
		return visitor.visit_assign(self)

class Binary(Expr):

	def __init__(self, left: Expr, operator: Token, right: Expr):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor: ExprVisitor)-> Any:
		return visitor.visit_binary(self)

class Grouping(Expr):

	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: ExprVisitor)-> Any:
		return visitor.visit_grouping(self)

class Literal(Expr):

	def __init__(self, value: Any):
		self.value = value

	def accept(self, visitor: ExprVisitor)-> Any:
		return visitor.visit_literal(self)

class Unary(Expr):

	def __init__(self, operator: Token, right: Expr):
		self.operator = operator
		self.right = right

	def accept(self, visitor: ExprVisitor)-> Any:
		return visitor.visit_unary(self)

class Variable(Expr):

	def __init__(self, name: Token):
		self.name = name

	def accept(self, visitor: ExprVisitor)-> Any:
		return visitor.visit_variable(self)