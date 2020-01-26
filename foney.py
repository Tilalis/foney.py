import sys
import readline

from atexit import register

from interpreter.builtins import namespace
from interpreter.money import Currency
from interpreter.parser import Parser

register(Currency.save)


def interpret(expression):
    try:
        parser = Parser(expression)
        node = parser.parse()
        result = node.traverse()

        namespace.set("_", result)
        return result
    except KeyError as key_error:
        print("Error: name {} is not defined".format(key_error))
    except Exception as exception:
        print("{}: {}".format(type(exception).__name__, str(exception)))


def from_file(filename):
    with open(filename, "r") as f:
        result = interpret(f)

    if result:
        print(result)


def interactive(prompt="foney> "):
    while True:
        try:
            expression = input(prompt)
            result = interpret(expression)
            if result:
                print(result)
        except (EOFError, KeyboardInterrupt):
            break


def main():
    if len(sys.argv) < 2:
        interactive()
    else:
        from_file(sys.argv[1])


if __name__ == '__main__':
    main()
