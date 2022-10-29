class DataPipelineOngoing(Exception):
    def __init__(self, *args):
        if not args:
            self.message = f"Provided data pipeline is already ongoing."
            self.pipeline_id = None
        else:
            self.message = f"Data pipeline {args[0]} is already ongoing."
            self.pipeline_id = args[0]

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
