from decimal import Decimal
from string import ascii_letters

from io import StringIO, IOBase
from typing import Union

from interpreter.tokens import Token, TokenType
from interpreter.money import Money, Currency, CurrencyStore


class Lexer:
    allowed_currency_chars = ascii_letters + CurrencyStore.aliases

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

    def number_currency_name(self):
        number = "".join(self.read_while(
            lambda s: s.isdigit() or s == '.'
        ))

        currency = "".join(self.read_while(
            lambda s: s in Lexer.allowed_currency_chars
        ))

        if not number:
            number = "".join(self.read_while(
                lambda s: s.isdigit() or s == '.'
            ))

        if number and currency:
            return Token(
                type=TokenType.MONEY,
                value=Money(
                    amount=Decimal(number),
                    currency=Currency(currency)
                )
            )

        if number:
            return Token(
                type=TokenType.NUMBER,
                value=Decimal(number)
            )

        # If no number, then it's name
        # TODO: Need to fix this
        if currency:
            return Token(
                TokenType.NAME,
                value=currency
            )

    def name(self):
        name = "".join(self.read_while(
            lambda s: s in ascii_letters
        ))

        return Token(
            type=TokenType.NAME,
            value=name
        )

    def __iter__(self):
        return self

    def __next__(self):
        if self._finished:
            raise StopIteration

        if not self._current:
            self._finished = True
            return Token(TokenType.EOF, None)

        if self._current.isspace():
            self.skip()

        number_currency_name = self.number_currency_name()
        if number_currency_name is not None:
            return number_currency_name

        token_type = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MUL,
            '/': TokenType.DIV,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '=': TokenType.SET
        }.get(self._current, None)

        if token_type:
            value = self._current
            self.read()

            return Token(token_type, value=value)

        return self.name()




