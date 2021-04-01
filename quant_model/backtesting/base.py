import numpy as np
import matplotlib.pyplot as plt


class BacktestMixin:

    def __init__(self):

        self.tc = None
        self.returns_col = None
        self.price_col = None
        self.data = None

    def _calculate_positions(self, data):
        raise NotImplementedError

    def _get_trades(self, data):
        raise NotImplementedError

    def _get_data(self):
        return self.data

    def _assess_strategy(self, data, title, plot_results=True):

        data = self._calculate_positions(data.copy())

        data["trades"] = data.position.diff().fillna(0).abs()

        data["strategy"] = data.position.shift(1) * data.returns
        data["strategy_tc"] = data["strategy"] - data.trades * self.tc

        data.dropna(inplace=True)

        data["creturns"] = data[self.returns_col].cumsum().apply(np.exp)
        data["cstrategy"] = data["strategy"].cumsum().apply(np.exp)
        data["cstrategy_tc"] = data["strategy_tc"].cumsum().apply(np.exp)

        number_trades = self._get_trades(data)

        print(f"Numer of trades: {number_trades}")

        self.results = data

        # absolute performance of the strategy
        perf = data["cstrategy_tc"].iloc[-1]

        # out-/underperformance of strategy
        outperf = perf - data["creturns"].iloc[-1]

        if plot_results:
            self.plot_results(title)

        return round(perf, 6), round(outperf, 6)

    def plot_results(self, title):
        """ Plots the cumulative performance of the trading strategy
        compared to buy and hold.
        """
        if self.results is None:
            print("No results to plot yet. Run a strategy first.")
        else:
            plotting_cols = ["creturns", "cstrategy", "position"]
            if self.tc != 0:
                plotting_cols.append("cstrategy_tc")

            ax = self.results[plotting_cols].plot(title=title, figsize=(12, 8), secondary_y='position')
            ax.right_ax.lines[0].set_alpha(0.4)
            plt.show()

    def _calculate_returns(self):
        self.data[self.returns_col] = np.log(self.data[self.price_col] / self.data[self.price_col].shift(1))
