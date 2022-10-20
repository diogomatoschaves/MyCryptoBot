class NoUnits(Exception):
    def __init__(self, *args):
        self.message = f"Can't close position with 0 units."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
