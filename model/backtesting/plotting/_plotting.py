import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

pio.renderers.default = "browser"


def plot_backtest_results(data, trades, with_tc=False):
    """
    Plots backtesting results for a trading strategy.

    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame containing the following columns:
        - 'accumulated_strategy_returns_tc': accumulated returns including trading costs
        - 'accumulated_returns': accumulated returns without trading costs
    trades : pandas.DataFrame
        DataFrame containing trade information, including the following columns:
        - 'entry_date': entry date of the trade
        - 'direction': direction of the trade (-1 for short, 1 for long)
        - 'profit': profit of the trade
        - 'units': size of the position
    with_tc : bool, optional
        Whether or not to plot equity without trading costs (default is False)

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
        name='Buy and Hold',
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

        # define a boolean column indicating if each trade is long or short
        trades['is_long'] = trades['direction'].apply(lambda x: x > 0)

        # define marker size as a percentage of position size
        marker_size = abs(trades['units']) / trades['units'].max() * 30

        # create separate traces for long and short trades
        fig.add_trace(go.Scatter(
            x=trades[trades['is_long']]["entry_date"], y=trades.loc[trades['is_long'], 'profit'],
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
            x=trades[~trades['is_long']]["entry_date"], y=trades.loc[~trades['is_long'], 'profit'],
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

    fig.update_layout(title='Backtesting Results',
                      xaxis_title='Date',
                      height=800,
                      showlegend=True)

    fig.update_yaxes(title_text='Value', row=1, col=1)
    fig.update_yaxes(title_text='Price', row=2, col=1)

    fig.show()
