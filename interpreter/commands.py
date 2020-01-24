import sys

from interpreter.namespace import Namespace


def operates_state(func):
    def command(*args, **kwargs):
        state = Namespace.state()
        return func(state, *args, **kwargs)

    return command


def command_exit(code=1):
    sys.exit(code)


@operates_state
def namespace(state):
    if state:
        print(
            "\n".join(
                "{name}: {value}".format(name=name, value=value)
                for name, value in state.items()
            )
        )


@operates_state
def show(state, name):
    value = state.get(name)
    if value:
        print("{} = {}".format(name, value))
    else:
        print("'{}' is not defined".format(name))


_commands = {
    '.exit': command_exit,
    '.namespace': namespace,
    '.show': show
}


class CommandError(BaseException):
    pass


def get(name):
    command = _commands.get(name)
    if command is None:
        raise CommandError("No such command: {}".format(name))

    return command
