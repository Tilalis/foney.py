from abc import ABCMeta, abstractmethod

from interpreter.namespace import Namespace
from interpreter.tokens import Token, TokenType

namespace = Namespace()


class AST(metaclass=ABCMeta):
    @abstractmethod
    def traverse(self):
        pass


class _Symbol(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def traverse(self):
        return self.value


class Number(_Symbol):
    def __init__(self, token):
        assert token.type == TokenType.NUMBER, "TokenType should be NUMBER"
        super().__init__(token)


class Money(_Symbol):
    def __init__(self, token):
        assert token.type == TokenType.MONEY, "TokenType should be MONEY"
        super().__init__(token)


class Name(_Symbol):
    def __init__(self, token):
        assert token.type == TokenType.NAME, "TokenType should be NAME"
        super().__init__(token)

    def traverse(self):
        return namespace.get(self.value)


class BinaryOperator(AST):
    def __init__(self, left, operator, right):
        assert isinstance(left, (Token, AST)), "left should be instance of TokenType or AST"
        assert isinstance(right, (Token, AST)), "left should be instance of TokenType or AST"

        assert operator.type in TokenType.binary_operators or operator.type == TokenType.SET, \
            "TokenType should be binary operator! {}".format(
                TokenType.binary_operators
            )

        self.left = left
        self.token = self.operator = operator
        self.right = right

    def traverse(self, operators=TokenType.binary_operators_map):
        operation = operators.get(self.token.type, None)

        if not operation:
            raise TypeError("Operation '{}' is not defined!".format(
                self.token.type
            ))

        return operation(
            self.left.traverse(),
            self.right.traverse()
        )


class Setter(BinaryOperator):
    def __init__(self, left, operator, right, setter=namespace.set):
        super().__init__(left, operator, right)
        self._setter = setter

    def traverse(self, operators=None):
        if not isinstance(self.left, Name):
            type_ = "Expression" if isinstance(self.left, AST) else self.left

            raise SyntaxError("{} cannot be used as Name".format(
                type_
            ))

        return self._setter(
            self.left.value,
            self.right.traverse()
        )
