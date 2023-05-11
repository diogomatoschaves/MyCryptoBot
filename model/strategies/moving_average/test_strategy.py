import ta
from model.strategies._mixin import StrategyMixin
from collections import OrderedDict


class BollingerBandsMACD(StrategyMixin):
    """
    Bollinger Bands with MACD Strategy

    Parameters
    ----------
    bb_length : int
        The length for Bollinger Bands calculation.
    bb_mult : float
        The standard deviation multiplier for Bollinger Bands.
    macd_short : int
        The short period for MACD calculation.
    macd_long : int
        The long period for MACD calculation.
    macd_signal : int
        The signal period for MACD calculation.
    data : pd.DataFrame, optional
        Dataframe of OHLCV data, by default None.
    **kwargs : dict, optional
        Additional keyword arguments to be passed to parent class, by default None.
    """

    def __init__(self, bb_length, bb_mult, macd_short, macd_long, macd_signal, data=None, **kwargs):
        self._bb_length = bb_length
        self._bb_mult = bb_mult
        self._macd_short = macd_short
        self._macd_long = macd_long
        self._macd_signal = macd_signal

        self.params = OrderedDict(bb_length=lambda x: int(x), bb_mult=lambda x: float(x),
                                  macd_short=lambda x: int(x), macd_long=lambda x: int(x),
                                  macd_signal=lambda x: int(x))

        StrategyMixin.__init__(self, data, **kwargs)

    def update_data(self, data):

        data = super().update_data(data)

        data['basis'] = ta.SMA(data['close'], self._bb_length)
        data['dev'] = data['close'].rolling(window=self._bb_length).std()
        data['dev2'] = self._bb_mult * data['dev']
        data['upper2'] = data['basis'] + data['dev2']
        data['lower2'] = data['basis'] - data['dev2']

        macd, signal, _ = ta.MACD(data['close'], self._macd_short, self._macd_long, self._macd_signal)
        data['macd'] = macd
        data['signal'] = signal

        return data

    def _calculate_positions(self, data):
        data['long_condition_bb'] = data['close'].gt(data['upper2'])
        data['short_condition_bb'] = data['close'].lt(data['lower2'])
        data['long_condition_macd'] = data['macd'].gt(data['signal'])
        data['short_condition_macd'] = data['macd'].lt(data['signal'])

        data['long_condition'] = data['long_condition_bb'] & data['long_condition_macd']
        data['short_condition'] = data['short_condition_bb'] & data['short_condition_macd']

        data['position'] = 0
        data.loc[data['long_condition'], 'position'] = 1
        data.loc[data['short_condition'], 'position'] = -1

        return data

    def get_signal(self, row=None):
        if row is None:
            return 0

        if row['long_condition']:
            return 1
        elif row['short_condition']:
            return -1
        else:
            return 0