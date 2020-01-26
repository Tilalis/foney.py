import sys

from interpreter.namespace import Namespace
from interpreter.money import Money, Currency

namespace = Namespace()


def _set_info(docs):
    def _set(fn):
        fn.name = fn.__name__.replace("_", "$")
        fn.repr = "[built-in function {}]".format(fn.name)
        fn.docs = docs.format(name=fn.name, repr=fn.repr)
        return fn

    return _set


@_set_info(
    ": {name} exits program\n"
    ": arguments: code -- exit code [optional]"
)
def _exit(code=1):
    sys.exit(code)


@_set_info(
    ": {name} shows current namespace"
)
def _namespace():
    print(
        "\n".join(
            "{name}: {value}".format(name=name, value=value)
            for name, value in namespace.items()
        )
    )


@_set_info(
    ": {name} shows variable value in the following format {{name}}={{value}}\n"
    ": arguments: name -- name from namespace"
)
def _show(name):
    value = namespace.get(name)
    if value:
        print("{} = {}".format(name, value))
    else:
        print("'{}' is not defined".format(name))


@_set_info(
    ": {name} shows all available built-in functions"
)
def _builtins():
    print("\n".join(
        "{name}: {value}".format(name=name, value=value.name)
        for name, value in namespace.builtins.get("functions", {}).items()
    ))


@_set_info(
    ": {name} deletes variable from namespace\n"
    ": arguments: name -- name from namespace"
)
def _delete(name):
    value = namespace.get(name)
    namespace.delete(name)
    return value


@_set_info(
    ": {name} returns second argument if first one is greater than zero, otherwise returns third one\n"
    ": arguments: value, true, false"
)
def _if(value, true, false):
    # Just PoC
    if value > 0:
        namespace.set("if", true)
        return true

    namespace.set("if", false)
    return false


@_set_info(
    ": {name} converts money to other currency\n"
    ": arguments: value, currency"
)
def _convert(value, to):
    if not isinstance(value, Money):
        raise Exception("Cannot convert non-Money!")

    if isinstance(to, Money):
        to = to._currency.name

    return value.convert(Currency(to))


@_set_info(
    ": {name} sets exchange rate for currencies\n"
    ": arguments: money, money"
)
def _exchange(first, second):
    assert isinstance(first, Money), "First argument should be Money!"
    assert isinstance(second, Money), "Second argument should be Money!"

    first_currency_name = first._currency.name
    second_currency_name = second._currency.name

    if first_currency_name == second_currency_name:
        raise Exception("Cannot set exchange rate for same currency!")

    first_amount = first._amount
    second_amount = second._amount

    # 2$ 4Br
    # 4Br 2$

    if first_amount < second_amount:
        first_to_second = second_amount / first_amount
        second_to_first = first_amount / second_amount
    else:
        first_to_second = first_amount / second_amount
        second_to_first = second_amount / first_amount

    Currency._exchange_rates.update({
        "{}_{}".format(first_currency_name, second_currency_name): first_to_second,
        "{}_{}".format(second_currency_name, first_currency_name): second_to_first
    })

    print("{} to {} is set to {}".format(first_currency_name, second_currency_name, first_to_second))
    print("{} to {} is set to {}".format(second_currency_name, first_currency_name, second_to_first))


@_set_info(
    ": {name} shows docstring for function\n"
    ": arguments: name -- function name"
)
def _doc(name):
    fn = namespace.builtins.get("functions", {}).get(name)
    if not fn:
        print("'{}' is not a builtin".format(name))
    else:
        print(fn.docs)


namespace.builtins = {
    "functions": {
        "$del": _delete,
        "$exit": _exit,
        "$show": _show,
        "$namespace": _namespace,
        "$if": _if,
        "$builtins": _builtins,
        "$convert": _convert,
        "$exchange": _exchange,
        "$doc": _doc
    }
}
