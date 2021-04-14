class InvalidInput(Exception):
    def __init__(self, *args):
        self.message = args[0] if args else "Invalid Input"

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
