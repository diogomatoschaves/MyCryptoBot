class LeverageSettingFail(Exception):
    def __init__(self, *args):
        if not args:
            self.message = "Failed to set leverage."

        self.message = f"Failed to set leverage. {args[0]}"

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
