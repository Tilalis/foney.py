from atexit import register

from interpreter import commands
from interpreter.money import Currency
from interpreter.parser import Parser

register(Currency.save)

if __name__ == "__main__":
    while True:
        try:
            expression = input("foney> ")

            if expression.startswith('.') or expression.startswith('#'):
                command, *arguments = expression.split(' ')
                command = commands.get(command.replace('#', '.'))
                command(*arguments)
            else:
                node = Parser(expression).parse()
                result = node.traverse()
                print(result)

        except EOFError:
            break
        except KeyError as key_error:
            print("Error: name {} is not defined".format(key_error))
        except commands.CommandError as command_error:
            print(command_error)
        except Exception as exception:
            print("{}: {}".format(type(exception).__name__, str(exception)))
