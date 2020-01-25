class Namespace:
    __shared__state__ = None

    def __init__(self):
        if Namespace.__shared__state__:
            self.__dict__ = Namespace.__shared__state__
        else:
            self._builtins = {}
            self._variables = {}

            Namespace.__shared__state__ = self.__dict__

    @staticmethod
    def state():
        return Namespace.__shared__state__

    @property
    def builtins(self):
        return self._builtins

    @builtins.setter
    def builtins(self, builtins):
        if not self._builtins:
            self._builtins = builtins
        else:
            raise Exception("You can only set builtins once!")

    def set(self, name, value):
        self._variables[name] = value
        return value

    def get(self, name):
        return self._variables[name]

    def items(self):
        return self._variables.items()
