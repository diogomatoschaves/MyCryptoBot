class InsufficientBalance(Exception):
    def __init__(self, *args):
        if not args:
            self.message = "Insufficient balance for starting pipeline."
        else:
            self.message = (f"Insufficient balance for starting pipeline. "
                            f"{args[0]} USDT is required and current balance is {args[1]} USDT.")

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
