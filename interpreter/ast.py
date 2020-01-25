from abc import ABCMeta, abstractmethod

from interpreter.namespace import Namespace
from interpreter.tokens import Token, TokenType

namespace = Namespace()


class AST(metaclass=ABCMeta):
    @abstractmethod
    def traverse(self):
        pass


class _Value(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def traverse(self):
        return self.value


class Number(_Value):
    def __init__(self, token):
        assert token.type == TokenType.NUMBER, "TokenType should be NUMBER"
        super().__init__(token)


class Money(_Value):
    def __init__(self, token):
        assert token.type == TokenType.MONEY, "TokenType should be MONEY"
        super().__init__(token)


class Symbol(_Value):
    def __init__(self, token):
        assert token.type == TokenType.SYMBOL, "TokenType should be SYMBOL"
        super().__init__(token)

    def traverse(self):
        return namespace.get(self.value)


class BinaryOperator(AST):
    def __init__(self, left, operator, right):
        assert isinstance(left, (Token, AST)), "left should be instance of TokenType or AST"
        assert isinstance(right, (Token, AST)), "left should be instance of TokenType or AST"

        assert operator.type in TokenType.binary_operators or operator.type == TokenType.ASSIGN, \
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


class Assign(BinaryOperator):
    def __init__(self, left, operator, right, setter=namespace.set):
        super().__init__(left, operator, right)
        self._setter = setter

    def traverse(self, operators=None):
        if not isinstance(self.left, Symbol):
            type_ = "Expression" if isinstance(self.left, AST) else self.left

            raise SyntaxError("{} cannot be used as Name".format(
                type_
            ))

        return self._setter(
            self.left.value,
            self.right.traverse()
        )


class Statements(AST):
    def __init__(self):
        self._nodes = []

    def add(self, node):
        assert isinstance(node, AST), "Node should be AST!"
        self._nodes.append(node)

    def traverse(self):
        for node in self._nodes[:-1]:
            node.traverse()

        if self._nodes:
            last_node = self._nodes[-1]
            return last_node.traverse()


class Apply(AST):
    def __init__(self, symbol=None):
        assert isinstance(symbol, Symbol), "Only symbols can be called!"

        self._fn = namespace.builtins.get("functions", {}).get(symbol.value)
        self._parameters = []
        self._result = symbol.traverse() if not self._fn else None
        self._symbol = symbol

    def add_parameter(self, parameter):
        assert isinstance(parameter, AST), "Parameter should be AST"
        self._parameters.append(parameter)

    def traverse(self):
        # TODO: Need to fix this
        parameters = [
            parameter.value if isinstance(parameter, _Value) else parameter.traverse()
            for parameter in self._parameters
        ]

        if self._result:
            if parameters:
                raise SyntaxError("Cannot call '{}' with parameters '{}', it's not a built-in function!".format(
                    self._symbol.value,
                    ", ".join(parameters)
                ))
            return self._result

        return self._fn(*parameters)
