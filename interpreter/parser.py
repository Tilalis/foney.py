from typing import Union

from interpreter.lexer import Lexer
from interpreter.tokens import TokenType
from interpreter.ast import Name, Number, Money, BinaryOperator, Setter


class Parser:
    def __init__(self, lexer: Union[Lexer, str]):
        self._lexer = lexer if isinstance(lexer, Lexer) else Lexer(lexer)
        self._current = next(self._lexer)

    def eat(self, token_type):
        if self._current.type == token_type:
            self._current = next(self._lexer)
        else:
            raise Exception("Invalid syntax on token: {}".format(self._current))

    def set(self):
        node = self.expr()
        token = self._current

        if token.type == TokenType.SET:
            self.eat(token.type)
            right = self.expr()
            node = Setter(
                left=node,
                operator=token,
                right=right
            )

        return node

    def expr(self):
        """
        set:    NAME SET expr
        expr:   term ((PLUS | MINUS) term)*"
        term:   factor ((MUL | DIV) factor)*"
        factor: (NUMBER | MONEY | NAME) | LPAREN expr RPAREN"
        """
        node = self.term()

        while self._current.type in (TokenType.PLUS, TokenType.MINUS):
            token = self._current
            self.eat(token.type)

            right = self.term()
            node = BinaryOperator(
                left=node,
                operator=token,
                right=right
            )

        return node

    def term(self):
        """term: factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self._current.type in (TokenType.MUL, TokenType.DIV):
            token = self._current
            self.eat(token.type)

            right = self.factor()
            node = BinaryOperator(
                left=node,
                operator=token,
                right=right
            )

        return node

    def factor(self):
        """factor: (NUMBER | MONEY | NAME) | LPAREN expr RPAREN"""
        token = self._current

        if token.type == TokenType.NAME:
            self.eat(token.type)
            return Name(token)

        if token.type in (TokenType.NUMBER, TokenType.MONEY):
            self.eat(token.type)

            if token.type == TokenType.NUMBER:
                return Number(token)

            return Money(token)

        if token.type == TokenType.RPAREN:
            self.eat(TokenType.RPAREN)
            node = self.expr()
            self.eat(TokenType.LPAREN)
            return node

    parse = set



