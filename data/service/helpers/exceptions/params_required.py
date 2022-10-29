class ParamsRequired(Exception):
    def __init__(self, *args):

        if not args:
            self.message = "The strategy parameters must be included in the request."
        else:
            self.message = f"{args[0]} are required parameters of the selected strategy."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
