import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from model.backtesting.helpers.metrics import get_drawdowns, get_dd_durations_limits

pio.renderers.default = "browser"


def plot_backtest_results(data, trades, offset=0, show_plot_no_tc=False, title=''):
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
    offset : int
        Offset for vertical margin of the plot.
    show_plot_no_tc : bool, optional
        Whether or not to plot equity without trading costs (default is False)
    title : str, optional
        Title to show on the backtesting results

    Returns
    -------
        None (displays plot using Plotly)

    """

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12)

    plot_equity_curves(fig, data, show_plot_no_tc)

    plot_trades(fig, trades)

    variable_offset = 25 * offset

    fig.update_layout(title=title, height=1000 + variable_offset, showlegend=True, margin=dict(t=80 + variable_offset))

    fig.update_layout(
        title={
            "yref": "container",
            "y": 0.97,
            "yanchor": "top"
        }
    )

    fig.update_yaxes(title_text='Value (USD)', row=1, col=1)
    fig.update_yaxes(title_text='Trade PnL (%)', row=2, col=1)

    fig.update_xaxes(row=1, col=1, title_text='Date', showticklabels=True, overwrite=True)
    fig.update_xaxes(row=2, col=1, title_text='Date', showticklabels=True, overwrite=True)

    fig.show()


def plot_equity_curves(fig, data, show_plot_no_tc):

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['accumulated_strategy_returns_tc'],
        name='Equity',
        line=dict(
            width=1.5,
            color='SteelBlue'
        )
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['accumulated_returns'],
        name='Buy & Hold',
        line=dict(
            color='Silver',
            width=1.5
        )
    ), row=1, col=1)

    if show_plot_no_tc:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['accumulated_strategy_returns'],
            name='Equity (no trading costs)',
            line=dict(
                width=0.8,
                color='Silver'
            )
        ), row=1, col=1)

    # plot drawdowns
    durations, limits = get_dd_durations_limits(data['accumulated_strategy_returns_tc'])

    x = []
    y = []
    for limit in limits:
        x.extend(limit)
        x.append(None)

        value = data['accumulated_strategy_returns_tc'][limit[0]]

        y.extend([value, value])
        y.append(None)

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        name='Drawdown',
        mode='lines',
        line=dict(
            color='Gold',
            width=1
        )
    ), row=1, col=1)

    # plot max drawdown duration
    max_duration_index = np.argmax(durations)

    start, end = limits[max_duration_index]
    value = data['accumulated_strategy_returns_tc'][start]

    fig.add_trace(go.Scatter(
        x=[start, end],
        y=[value, value],
        name=f'Max Drawdown Duration',
        mode='lines',
        line=dict(
            color='Red',
            width=1
        )
    ), row=1, col=1)

    # plot peak equity point
    peak_index = data['accumulated_strategy_returns_tc'].argmax()
    peak_time = data.index[peak_index]
    peak_value = data['accumulated_strategy_returns_tc'][peak_index]

    fig.add_trace(go.Scatter(
        x=[peak_time],
        y=[peak_value],
        name='Peak',
        mode='markers',
        marker=dict(
            color='MediumBlue',
            size=8
        )
    ), row=1, col=1)

    # Plot lowest equity point
    low_index = data['accumulated_strategy_returns_tc'].argmin()
    low_time = data.index[low_index]
    low_value = data['accumulated_strategy_returns_tc'][low_index]

    fig.add_trace(go.Scatter(
        x=[low_time],
        y=[low_value],
        name='Lowest',
        mode='markers',
        marker=dict(
            color='Maroon',
            size=8
        )
    ), row=1, col=1)

    # Plot max drawdown
    drawdowns = get_drawdowns(data['accumulated_strategy_returns_tc'])

    max_drawdown_index = drawdowns.argmin()
    max_drawdown_time = drawdowns.index[max_drawdown_index]
    max_drawdown_equity = data['accumulated_strategy_returns_tc'][max_drawdown_index]
    max_drawdown_value = drawdowns[max_drawdown_index]

    fig.add_trace(go.Scatter(
        x=[max_drawdown_time],
        y=[max_drawdown_equity],
        name=f'Max Drawdown ({round(max_drawdown_value * 100, 1)} %)',
        mode='markers',
        marker=dict(
            color='Crimson',
            size=7
        )
    ), row=1, col=1)


def plot_trades(fig, trades):

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
