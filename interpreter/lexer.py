from decimal import Decimal
from string import ascii_letters

from io import StringIO, IOBase
from typing import Union

from interpreter.tokens import Token, TokenType
from interpreter.money import Money, Currency, CurrencyStore


class Lexer:
    allowed_currency_chars = list(ascii_letters) + CurrencyStore.aliases + ["$", "_"]

    def __init__(self, stream: Union[IOBase, str]):
        if isinstance(stream, str):
            stream = StringIO(stream)

        self._finished = False
        self._stream = stream
        self._current = self._stream.read(1)

    def read(self):
        self._current = self._stream.read(1)
        return self._current

    def read_while(self, predicate):
        while self._current:
            if predicate(self._current):
                yield self._current
                self.read()
            else:
                break

    def skip(self):
        while self._current and self._current.isspace():
            self.read()

    def symbol(self):
        digits = "".join(self.read_while(
            lambda s: s.isdigit() or s == '.'
        ))

        alphanumeric = "".join(self.read_while(
            lambda s: s in Lexer.allowed_currency_chars
        ))

        if not digits:
            digits = "".join(self.read_while(
                lambda s: s.isdigit() or s == '.'
            ))

        if digits and alphanumeric:
            return Token(
                type=TokenType.MONEY,
                value=Money(
                    amount=Decimal(digits),
                    currency=Currency(alphanumeric)
                )
            )

        if digits:
            return Token(
                type=TokenType.NUMBER,
                value=Decimal(digits)
            )

        # If no number, then it's name
        # TODO: Need to fix this
        if alphanumeric:
            return Token(
                TokenType.SYMBOL,
                value=alphanumeric
            )

    def __iter__(self):
        return self

    def __next__(self):
        if self._finished:
            raise StopIteration

        if not self._current:
            self._finished = True
            return Token(TokenType.EOF, None)

        if self._current != '\n' and self._current.isspace():
            self.skip()

        symbol = self.symbol()
        if symbol is not None:
            return symbol

        token_type = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MUL,
            '/': TokenType.DIV,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            ';': TokenType.DELIMITER,
            '\n': TokenType.DELIMITER,
            '=': TokenType.ASSIGN
        }.get(self._current, None)

        if token_type:
            value = self._current
            self.read()

            return Token(token_type, value=value)

        print("Should not get here")
