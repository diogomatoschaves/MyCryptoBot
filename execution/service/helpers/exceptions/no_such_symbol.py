class NoSuchSymbol(Exception):
    def __init__(self, *args):
        if not args:
            self.message = f"Symbol was not found."

        self.message = f"Symbol {args[0]} was not found."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
