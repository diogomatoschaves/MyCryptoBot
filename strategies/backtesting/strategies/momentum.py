

class MomentumBase:
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self):
        self.data = None
        self.window = None
        self.symbol = None

    def __repr__(self):
        return "{}(symbol = {}, window = {})".format(self.__class__.__name__, self.symbol, self.window)

    def _update_data(self):
        """ Retrieves and prepares the data.
        """
        pass

    def _set_parameters(self, window):
        """ Updates SMA parameters and resp. time series.
        """
        if window is not None:
            self.window = int(window)