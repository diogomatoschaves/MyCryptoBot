class ColorRequired(Exception):
    def __init__(self, *args):

        self.message = "Parameter 'color' is required."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
