from typing import Union

from interpreter.lexer import Lexer
from interpreter.tokens import TokenType
from interpreter.ast import Symbol, Number, Money, BinaryOperator, Assign


class Parser:
    def __init__(self, lexer: Union[Lexer, str]):
        self._lexer = lexer if isinstance(lexer, Lexer) else Lexer(lexer)
        self._current = next(self._lexer)

    def eat(self, token_type):
        if self._current.type == token_type:
            self._current = next(self._lexer)
        else:
            raise Exception("Invalid syntax on token: {}".format(self._current))

    def expr(self):
        """
        expr:   term ((PLUS | MINUS) term)* | SYMBOL ASSIGN expr"
        term:   factor ((MUL | DIV) factor)*"
        factor: (NUMBER | MONEY | SYMBOL) | LPAREN expr RPAREN"
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

        if self._current.type == TokenType.ASSIGN:
            token = self._current
            self.eat(self._current.type)

            node = Assign(
                left=node,
                operator=token,
                right=self.expr()
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
        """factor: (NUMBER | MONEY | SYMBOL) | LPAREN expr RPAREN"""
        token = self._current

        if token.type in (TokenType.NUMBER, TokenType.MONEY):
            self.eat(token.type)

            if token.type == TokenType.NUMBER:
                return Number(token)

            return Money(token)

        if token.type == TokenType.SYMBOL:
            self.eat(token.type)
            return Symbol(token)

        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node

    parse = expr



