from __future__ import annotations
from dataclasses import dataclass, field
import enum

@dataclass
class Token:
    token_type: Tok
    lexeme: str
    start: int
    line: int
    length: int = 1
    n_newlines: int = 0


class Tok(enum.Enum):
    # Single-character tokens
    LEFT_PAREN = enum.auto()
    RIGHT_PAREN = enum.auto()
    LEFT_BRACE = enum.auto()
    RIGHT_BRACE = enum.auto()
    COMMA = enum.auto()
    DOT = enum.auto()
    MINUS = enum.auto()
    PLUS = enum.auto()
    SEMICOLON = enum.auto()
    SLASH = enum.auto()
    STAR = enum.auto()
    # One or two character tokens
    BANG = enum.auto()
    BANG_EQUAL = enum.auto()
    EQUAL = enum.auto()
    EQUAL_EQUAL = enum.auto()
    GREATER = enum.auto()
    GREATER_EQUAL = enum.auto()
    LESS = enum.auto()
    LESS_EQUAL = enum.auto()
    # Literals
    IDENTIFIER = enum.auto()
    STRING = enum.auto()
    NUMBER = enum.auto()
    COMMENT = enum.auto()
    # Keywords
    AND = enum.auto()
    CLASS = enum.auto()
    ELSE = enum.auto()
    FALSE = enum.auto()
    FUN = enum.auto()
    FOR = enum.auto()
    IF = enum.auto()
    NIL = enum.auto()
    OR = enum.auto()
    PRINT = enum.auto()
    RETURN = enum.auto()
    SUPER = enum.auto()
    THIS = enum.auto()
    TRUE = enum.auto()
    VAR = enum.auto()
    WHILE = enum.auto()
    # Whitespace
    WHITESPACE = enum.auto()
    # End of File
    EOF = enum.auto()
