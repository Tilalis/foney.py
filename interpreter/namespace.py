class Namespace:
    __shared__state__ = None

    def __init__(self):
        if Namespace.__shared__state__:
            self.__dict__ = Namespace.__shared__state__
        else:
            Namespace.__shared__state__ = self.__dict__

    @staticmethod
    def state():
        return Namespace.__shared__state__

    def set(self, name, value):
        self.__dict__[name] = value
        return value

    def get(self, name):
        return self.__dict__[name]
