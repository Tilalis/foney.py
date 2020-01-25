import sys

from atexit import register

from interpreter import commands
from interpreter.namespace import Namespace
from interpreter.money import Currency
from interpreter.parser import Parser

register(Currency.save)
namespace = Namespace()


def interpret(expression):
    try:
        node = Parser(expression).parse()
        result = node.traverse()
        namespace.set("_", result)
        return result
    except KeyError as key_error:
        print("Error: name {} is not defined".format(key_error))
    except commands.CommandError as command_error:
        print(command_error)
    except Exception as exception:
        print("{}: {}".format(type(exception).__name__, str(exception)))


def from_file(filename):
    result = None
    with open(filename, "r") as f:
        # TODO: Fix this
        for line in f:
            result = interpret(line)

    print(result)


def interactive(prompt="foney> "):
    while True:
        try:
            expression = input(prompt)

            if expression.startswith('.') or expression.startswith('#'):
                command, *arguments = expression.split(' ')
                command = commands.get(command.replace('#', '.'))
                command(*arguments)
            else:
                result = interpret(expression)

                if result:
                    print(result)

        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    if len(sys.argv) < 2:
        interactive()
    else:
        from_file(sys.argv[1])

