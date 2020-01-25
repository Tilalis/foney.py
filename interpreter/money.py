import os
import json
import typing

from string import ascii_letters

from datetime import date
from decimal import Decimal

import requests


class CurrencyStore(type):
    _store = {}

    _aliases = {
        "$": "USD",
        "€": "EUR",
        "₽": "RUB",
        "Br": "BYN"
    }

    aliases = list(_aliases.keys())

    def __call__(cls, name, *args, **kwargs):
        alias = CurrencyStore._aliases.get(name, None)

        if alias:
            alias, name = name, alias

        obj = CurrencyStore._store.get(name, None)

        if obj is not None:
            return obj

        obj = type.__call__(cls, name, alias, *args, **kwargs)
        CurrencyStore._store[name] = obj

        return obj


API_KEY = "9b9535c8007716ed626b"


class Currency(metaclass=CurrencyStore):
    _muted = False

    _folder = "rates"
    _filename = "exchange_rates.{}.json".format(date.today())

    _exchange_rates = {}

    def __init__(self, name: str, alias: str = None):
        assert isinstance(name, str), "Name should be string!"

        if len(name) != 3 or any(ch not in ascii_letters for ch in name):
            raise NameError("invalid currency name '{}'".format(name))

        self._name = name.upper()
        self._alias = alias
        self._use_alias = bool(alias)

    @property
    def name(self):
        return self._name

    @property
    def use_alias(self):
        return self._use_alias

    @staticmethod
    def mute():
        Currency._muted = True

    @staticmethod
    def exchange_rate(fr: "Currency", to: "Currency"):
        from_to = "{}_{}".format(fr._name, to._name)
        rate = Currency._exchange_rates.get(from_to, None)

        if rate:
            return rate

        if not Currency._muted:
            print("Loading {} to {} exchange rate...".format(
                fr._name,
                to._name
            ))

        to_from = "{}_{}".format(to._name, fr._name)

        url = "https://{status}.currconv.com/api/v7/convert?q={from_to},{to_from}&compact=ultra&apiKey={api_key}".format(
            status="free",
            from_to=from_to,
            to_from=to_from,
            api_key=API_KEY
        )

        response = requests.get(url)
        if response.ok:
            Currency._exchange_rates.update(response.json())
            Currency.save()

            return Currency._exchange_rates[from_to]
        else:
            raise ConnectionError("Could not connect to API!")

    def __str__(self):
        return self._alias if self._alias else self._name

    @staticmethod
    def save():
        if not os.path.isdir(Currency._folder):
            os.mkdir(Currency._folder)

        with open(os.path.join(Currency._folder, Currency._filename), "w") as f:
            json.dump(Currency._exchange_rates, f)

    @staticmethod
    def load():
        if Currency._exchange_rates:
            return

        path = os.path.join(Currency._folder, Currency._filename)
        if not os.path.exists(path):
            return

        with open(path, "r") as f:
            Currency._exchange_rates = json.load(f)

    @staticmethod
    def reload():
        Currency._exchange_rates = {}
        Currency.load()


Currency.load()


class Money:
    def __init__(self, amount: str, currency: typing.Union[Currency, str]):
        assert isinstance(amount, (str, Decimal)), "Money amount should be string or Decimal!"
        assert isinstance(currency, (Currency, str)), "Currency should be of Currency or string type!"

        self._amount = Decimal(amount) if isinstance(amount, Decimal) else amount
        self._currency = currency if isinstance(currency, Currency) else Currency(currency)

    def convert(self, to_currency: Currency):
        rate = Currency.exchange_rate(
            fr=self._currency,
            to=to_currency
        )

        new_amount = round(self._amount * Decimal(rate), 2)

        return Money(
            amount=new_amount,
            currency=to_currency
        )

    def _convert_other(self, other: "Money"):
        if not isinstance(other, Money):
            return None

        if self._currency != other._currency:
            return other.convert(to_currency=self._currency)
        else:
            return other

    def __add__(self, other):
        other = self._convert_other(other)

        if not other:
            raise TypeError("Cannot add bare numbers to Money!")

        return Money(self._amount + other._amount, self._currency)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        other = self._convert_other(other)

        if not other:
            raise TypeError("Cannot substitute bare numbers from Money and vice versa!")

        return Money(self._amount - other._amount, self._currency)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        assert isinstance(other, (Decimal, int, float)), "Type of non-money argument should be Decimal, int or float!"

        other = Decimal(other)
        return Money(round(self._amount * other, 2), self._currency)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        assert isinstance(other, (Decimal, int, float)), "Type of non-money argument should be Decimal, int or float!"

        other = Decimal(other)
        return Money(round(self._amount / other, 2), self._currency)

    def __gt__(self, other: typing.Union["Money", int, float, Decimal]):
        if isinstance(other, (int, float, Decimal)):
            return self._amount > other

        other = self._convert_other(other)
        return self._amount > other._amount

    def __eq__(self, other: typing.Union["Money", int, float, Decimal]):
        if isinstance(other, (int, float, Decimal)):
            return self._amount == other

        other = self._convert_other(other)
        return self._amount == other._amount

    def __str__(self):
        if self._currency.use_alias:
            return "{}{}".format(self._currency, self._amount)

        return "{}{}".format(self._amount, self._currency)

    def __repr__(self):
        return self.__str__()

