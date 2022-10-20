class PipelineNotActive(Exception):
    def __init__(self, *args):
        if not args:
            self.message = "Pipeline is not active."

        self.message = f"Pipeline {args[0]} is not active."

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
