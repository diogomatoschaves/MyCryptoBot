class ParamsInvalid(Exception):
    def __init__(self, *args):
        if not args:
            self.message = f"Parameters are not valid."
        else:
            self.message = f"{args[0]} are not valid parameters."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
