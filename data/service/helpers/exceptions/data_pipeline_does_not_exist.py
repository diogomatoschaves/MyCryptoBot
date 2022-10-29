class DataPipelineDoesNotExist(Exception):
    def __init__(self, *args):
        if not args:
            self.message = f"Provided data pipeline does not exist."
        else:
            self.message = f"Data pipeline {args[0]} does not exist."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
