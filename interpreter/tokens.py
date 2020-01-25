import operator

from enum import Enum
from typing import NamedTuple, Any


class TokenType(Enum):
    NUMBER = 1
    MONEY = 2

    PLUS = 3
    MINUS = 4
    MUL = 5
    DIV = 6

    LPAREN = 7
    RPAREN = 8

    SYMBOL = 9
    SET = 10

    EOF = 11

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


TokenType.binary_operators_map = {
    TokenType.PLUS: operator.add,
    TokenType.MINUS: operator.sub,
    TokenType.MUL: operator.mul,
    TokenType.DIV: operator.truediv
}

TokenType.binary_operators = (
    TokenType.PLUS,
    TokenType.MINUS,
    TokenType.MUL,
    TokenType.DIV,
)


class Token(NamedTuple):
    type: TokenType
    value: Any
