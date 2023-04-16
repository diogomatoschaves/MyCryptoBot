import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

pio.renderers.default = "browser"


def plot_backtest_results(data, trades, with_tc=False, title=''):
    """
    Plots backtesting results for a trading strategy.

    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame containing the following columns:
        - 'accumulated_strategy_returns_tc': accumulated returns including trading costs
        - 'accumulated_strategy_returns': accumulated returns without trading costs
        - 'accumulated_returns': accumulated returns without trading costs
    trades : pandas.DataFrame
        DataFrame containing trade information, including the following columns:
        - 'entry_date': entry date of the trade
        - 'direction': direction of the trade (-1 for short, 1 for long)
        - 'profit': profit of the trade
        - 'units': size of the position
    with_tc : bool, optional
        Whether or not to plot equity without trading costs (default is False)
    title : str, optional
        Title to show on the backtesting results

    Returns
    -------
        None (displays plot using Plotly)

    """

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['accumulated_strategy_returns_tc'],
        name='Equity',
        line=dict(
            width=1.5,
            color='LightGreen'
        )
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['accumulated_returns'],
        name='Buy & Hold',
        line=dict(
            color='PaleVioletRed',
            width=1.5
        )
    ), row=1, col=1)

    if with_tc:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['accumulated_strategy_returns'],
            name='Equity (no trading costs)',
            line=dict(
                width=0.8,
                color='Silver'
            )
        ), row=1, col=1)

    if len(trades) > 0:

        trades["pnl_pct"] = np.round(trades["pnl"] * 100, 2)

        # define a boolean column indicating if each trade is long or short
        trades['is_long'] = trades['direction'].apply(lambda x: x > 0)

        # define marker size as a percentage of position size
        position_size = trades['units'] * trades["entry_price"]

        marker_size = abs(position_size) / position_size.max() * 30

        # create separate traces for long and short trades
        fig.add_trace(go.Scatter(
            x=trades[trades['is_long']]["entry_date"], y=trades.loc[trades['is_long'], 'pnl_pct'],
            name='Long', mode='markers', marker=dict(
                symbol='triangle-up',
                color='limegreen',
                size=marker_size[trades['is_long']],
                line=dict(
                    color='Black',
                    width=1
                )
            )
        ), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=trades[~trades['is_long']]["entry_date"], y=trades.loc[~trades['is_long'], 'pnl_pct'],
            name='Short', mode='markers', marker=dict(
                symbol='triangle-down',
                color='red',
                size=marker_size[~trades['is_long']],
                line=dict(
                    color='White',
                    width=1
                )
            )
        ), row=2, col=1)

    fig.update_layout(title=f'Backtesting Results: {title}',
                      xaxis_title='Date',
                      height=800,
                      showlegend=True)

    fig.update_yaxes(title_text='Value (USD)', row=1, col=1)
    fig.update_yaxes(title_text='Trade PnL (%)', row=2, col=1)

    fig.show()
