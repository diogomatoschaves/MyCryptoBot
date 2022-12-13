class PipelineStartFail(Exception):
    def __init__(self, *args):
        if not args:
            self.message = f"Pipeline start failed."
        else:
            self.message = args[0]

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
