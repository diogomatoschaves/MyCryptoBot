class NegativeEquity(Exception):
    def __init__(self, *args):
        if not args:
            self.message = "Pipeline has reached negative equity."

        self.message = f"Pipeline {args[0]} has reached negative equity."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
