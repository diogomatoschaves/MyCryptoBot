class OptimizationParametersInvalid(Exception):
    def __init__(self, *args):
        if not args:
            self.message = f"Optimization parameters are not valid."
        else:
            self.message = f"{args[0]} optimization parameters are not valid."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
