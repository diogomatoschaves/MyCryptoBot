class NameInvalid(Exception):
    def __init__(self, *args):
        if not args:
            self.message = f"Chosen name is not valid is already taken."
        else:
            self.message = f"{args[0]} is not a valid name or is already taken."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
