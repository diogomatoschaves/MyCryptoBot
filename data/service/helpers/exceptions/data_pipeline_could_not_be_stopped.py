class DataPipelineCouldNotBeStopped(Exception):
    def __init__(self, *args):
        if not args:
            self.message = f"The Pipeline could not be stopped"
        else:
            self.message = f"Data pipeline could not be stopped. {args[0]}"

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
