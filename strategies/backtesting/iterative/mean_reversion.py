from strategies.backtesting.iterative.base import IterativeBacktester
from strategies.backtesting.strategies import MeanRevBase


class MeanRevIterBacktester(MeanRevBase, IterativeBacktester):

    def __init__(self, data, amount, ma, sd, trading_costs=0, symbol='BTCUSDT'):
        MeanRevBase.__init__(self)
        IterativeBacktester.__init__(
            self,
            data,
            amount,
            symbol=symbol,
            trading_costs=trading_costs
        )

        self.ma = ma
        self.sd = sd
        self.results = None

        self._update_data()

    def test_strategy(self, ma_sd_pair=None, plot_results=True):
        """ Test a mean-reversion strategy (bollinger) with SMA and dev.
        """

        self._set_parameters(ma_sd_pair)
        self._reset_object()

        ma = self.ma
        sd = self.sd

        # nice printout
        print("-" * 75)
        print("Testing Bollinger Bands Strategy: {} | ma = {} & sd = {}".format(self.symbol, ma, sd))
        print("-" * 75)

        data = self.data.dropna().copy()
        
        # Bollinger strategy
        for bar, (timestamp, row) in enumerate(data.iloc[:-1].iterrows()):  # all bars (except the last bar)

            date, price = self.get_values(data, bar)
            
            if self.position == 0: # when neutral
                if row[self.price_col] < row["lower"]:  # signal to go long
                    self.go_long(date, price, amount="all")  # go long with full amount
                    self.position = 1  # long position
                elif row[self.price_col] > row["upper"]:  # signal to go Short
                    self.go_short(date, price, amount="all")  # go short with full amount
                    self.position = -1  # short position
            elif self.position == 1:  # when long
                if row[self.price_col] > row["sma"]:
                    if row[self.price_col] > row["upper"]:  # signal to go short
                        self.go_short(date, price, amount="all")  # go short with full amount
                        self.position = -1  # short position
                    else:
                        self.sell_instrument(date, price, units=self.units)  # go neutral
                        self.position = 0
            elif self.position == -1: # when short
                if row[self.price_col] < row["sma"]:
                    if row[self.price_col] < row["lower"]:  # signal to go long
                        self.go_long(date, price, amount="all")  # go long with full amount
                        self.position = 1  # long position
                    else:
                        self.buy_instrument(date, price, units=-self.units)  # go neutral
                        self.position = 0

            self.positions.append(self.position)

        self.close_pos(data, bar+1)  # close position at the last bar

        self.positions.append(0)

        title = self.__repr__()

        return self._assess_strategy(data, title, plot_results)