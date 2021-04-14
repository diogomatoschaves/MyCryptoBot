import numpy as np
import matplotlib.pyplot as plt


class BacktestMixin:

    def __init__(self, symbol, trading_costs):

        self.symbol = symbol
        self.tc = trading_costs / 100

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
            print("No results to plot yet. Run the strategy first.")
        else:
            plotting_cols = ["creturns"]
            if self.tc != 0:
                plotting_cols.append("cstrategy")

            ax = self.results[plotting_cols].plot(title=title, figsize=(20, 12))

            # Convert labels to colors
            label2color = {
                1: 'green',
                0: 'brown',
                -1: 'red',
            }
            self.results['color'] = self.results['position'].apply(lambda label: label2color[label])

            # Add px_last lines
            for color, start, end in self.gen_repeating(self.results['color']):
                if start > 0: # make sure lines connect
                    start -= 1
                idx = self.results.index[start:end+1]
                self.results.loc[idx, 'cstrategy_tc'].plot(ax=ax, color=color, label='')
                self.results.loc[idx, ['position']].plot(ax=ax, color=color, label='', secondary_y='position', alpha=0.3)

            # Get artists and labels for legend and chose which ones to display
            handles, labels = ax.get_legend_handles_labels()

            # Create custom artists
            g_line = plt.Line2D((0, 1), (0, 0), color='green')
            y_line = plt.Line2D((0, 1), (0, 0), color='brown')
            r_line = plt.Line2D((0, 1), (0, 0), color='red')

            # Create legend from custom artist/label lists
            ax.legend(
                handles + [g_line, y_line, r_line],
                labels + [
                    'long position',
                    'neutral_position',
                    'short position',
                ],
                loc='best',
            )

            plt.show()

    @staticmethod
    def gen_repeating(s):
        """Generator: groups repeated elements in an iterable
        E.g.
            'abbccc' -> [('a', 0, 0), ('b', 1, 2), ('c', 3, 5)]
        """
        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]:
                j += 1
            yield (s[i], i, j-1)
            i = j

    @staticmethod
    def plot_func(ax, group):
        color = 'r' if (group['position'] < 0).all() else 'g'
        lw = 2.0
        ax.plot(group.index, group.cstrategy_tc, c=color, linewidth=lw)
