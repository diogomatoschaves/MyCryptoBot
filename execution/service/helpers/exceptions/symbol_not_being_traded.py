class SymbolNotBeingTraded(Exception):
    def __init__(self, *args):
        if not args:
            self.message = f"Symbol is not being traded."

        self.message = f"{args[0]} is not being traded."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
