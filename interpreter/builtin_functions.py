import sys

from interpreter.namespace import Namespace
from interpreter.money import Money, Currency

namespace = Namespace()


def _set_repr(fn):
    def _repr(self):
        def _r():
            return "[built-in function '{}']".format(self.__name__.replace("_", "$"))
        return _r

    fn.repr = _repr(fn)
    return fn


@_set_repr
def _exit(code=1):
    sys.exit(code)


@_set_repr
def _namespace():
    print(
        "\n".join(
            "{name}: {value}".format(name=name, value=value)
            for name, value in namespace.items()
        )
    )


@_set_repr
def _show(name):
    value = namespace.get(name)
    if value:
        print("{} = {}".format(name, value))
    else:
        print("'{}' is not defined".format(name))


@_set_repr
def _builtins():
    print("\n".join(
        "{name}: {value}".format(name=name, value=value.repr())
        for name, value in namespace.builtins.get("functions", {}).items()
    ))


@_set_repr
def _delete(name):
    value = namespace.get(name)
    namespace.delete(name)
    return value


@_set_repr
def _if(value, true, false):
    # Just PoC
    if value > 0:
        namespace.set("if", ">")
        return true

    namespace.set("if", "<")
    return false


@_set_repr
def _convert(value, to):
    if not isinstance(value, Money):
        raise Exception("Cannot convert non-Money!")

    if isinstance(to, Money):
        to = to._currency.name

    return value.convert(Currency(to))


namespace.builtins = {
    "functions": {
        "$del": _delete,
        "$exit": _exit,
        "$show": _show,
        "$namespace": _namespace,
        "$if": _if,
        "$builtins": _builtins,
        "$convert": _convert
    }
}
