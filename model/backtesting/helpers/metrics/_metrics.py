from functools import reduce
from typing import List

import numpy as np
import pandas as pd

from model.backtesting.helpers import Trade


def exposure_time(positions: np.ndarray) -> float:
    """Calculate the percentage of time the strategy was exposed to the market."""
    return np.count_nonzero(positions) / len(positions) * 100


def equity_final(equity_curve: np.ndarray) -> float:
    """Calculate the final equity value."""
    return equity_curve[-1]


def equity_peak(equity_curve: np.ndarray) -> float:
    """Calculate the peak equity value."""
    return np.max(equity_curve)


def return_pct(equity_curve: np.ndarray) -> float:
    """Calculate the total return percentage."""
    return (equity_curve[-1] / equity_curve[0] - 1) * 100


def annual_return_pct(cum_returns: pd.Series) -> float:
    """Calculate the annualized return percentage."""

    years_df = cum_returns.resample('1Y').count()

    return ((cum_returns[-1] / cum_returns[0])**(1 / len(years_df))-1) * 100


def annual_volatility_pct(returns: pd.Series) -> float:
    """Calculate the annualized volatility percentage."""

    days_df = returns.resample('1D').sum()

    return np.std(days_df) * np.sqrt(365) * 100


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0) -> float:
    """Calculate the Sharpe ratio."""
    excess_returns = returns - risk_free_rate
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(365)


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0) -> float:
    """Calculate the Sortino ratio."""
    downside_returns = returns[returns < risk_free_rate]
    downside_volatility = np.std(downside_returns) * np.sqrt(365)
    excess_returns = returns - risk_free_rate
    return np.mean(excess_returns) / downside_volatility


def calmar_ratio(cum_returns: pd.Series, risk_free_rate: float = 0) -> float:
    """Calculate the Calmar ratio."""
    max_drawdown = max_drawdown_pct(cum_returns)
    annual_return = annual_return_pct(cum_returns)
    return (annual_return - risk_free_rate) / max_drawdown


def max_drawdown_pct(cum_returns: pd.Series) -> float:
    """Calculate the maximum drawdown percentage."""
    peaks = np.maximum.accumulate(cum_returns)
    drawdowns = (cum_returns - peaks) / peaks

    return np.min(drawdowns) * 100


def avg_drawdown_pct(cum_returns: pd.Series) -> float:
    """Calculate the average drawdown percentage."""
    peaks = np.maximum.accumulate(cum_returns)
    drawdowns = (cum_returns - peaks) / peaks

    drawdown_maximums = []
    drawdown_period = []

    is_zero = True
    for dd in drawdowns:
        if dd == 0:
            if not is_zero:
                drawdown_maximums.append(np.min(drawdown_period))
            is_zero = True
        else:
            if is_zero:
                drawdown_period = []
                is_zero = False
            else:
                drawdown_period.append(dd)

    if len(drawdown_period) != 0:
        drawdown_maximums.append(np.min(drawdown_period))

    return np.mean(drawdown_maximums) * 100


def max_drawdown_duration(cum_returns: pd.Series) -> int:
    """Calculate the duration of the maximum drawdown in terms of the period between peak to peak.

    Parameters
    ----------
    cum_returns : pd.Series
        An array of cumulative returns.

    Returns
    -------
    int
        The duration of the maximum drawdown between peak to peak in the used time unit.
    """
    peak_index = 0
    max_drawdown_dur = 0
    for i in range(1, len(cum_returns)):
        if cum_returns[i] > cum_returns[peak_index]:
            peak_index = i
        else:
            drawdown_duration = i - peak_index
            if drawdown_duration > max_drawdown_dur:
                max_drawdown_dur = drawdown_duration
    return max_drawdown_dur


def avg_drawdown_duration(cum_returns: np.ndarray) -> float:
    """Calculate the average duration of drawdowns."""
    peak_index = 0
    drawdown_duration = 0

    durations = []

    drawdown = False
    for i in range(1, len(cum_returns)):
        if cum_returns[i] > cum_returns[peak_index]:
            peak_index = i

            if drawdown:
                durations.append(drawdown_duration)
                drawdown = False
        else:
            drawdown = True
            drawdown_duration = i - peak_index

    if drawdown:
        durations.append(drawdown_duration)

    return np.mean(durations)


def win_rate_pct(trades: List[Trade]) -> float:
    """Calculate the percentage of winning trades."""
    winning_trades = reduce(
        lambda accum, trade: accum + 1 if (trade.exit_price - trade.entry_price) * trade.direction > 0 else accum,
        trades,
        0
    )

    return winning_trades / len(trades) * 100


def best_trade_pct(trades: List[Trade]) -> float:
    """Calculate the percentage of the best trade."""

    best_trade = reduce(
        lambda accum, trade: (trade.exit_price - trade.entry_price) / trade.entry_price * trade.direction
        if (trade.exit_price - trade.entry_price) / trade.entry_price * trade.direction > accum
        else accum,
        trades,
        0
    )
    return best_trade * 100


def worst_trade_pct(trades: List[Trade]) -> float:
    """Calculate the percentage of the worst trade."""
    worst_trade = reduce(
        lambda accum, trade: (trade.exit_price - trade.entry_price) / trade.entry_price * trade.direction
        if (trade.exit_price - trade.entry_price) / trade.entry_price * trade.direction < accum
        else accum,
        trades,
        0
    )
    return worst_trade * 100


def avg_trade_pct(trades: List[Trade]) -> float:
    """Calculate the average trade percentage."""
    trades_pct = reduce(
        lambda accum, trade: (trade.exit_price - trade.entry_price) / trade.entry_price * trade.direction,
        trades,
        []
    )
    return np.mean(trades_pct)


def max_trade_duration(trades: List[Trade]) -> int:
    """Calculate the duration of the longest trade."""
    durations = map(
        lambda trade: (trade.exit_date - trade.entry_date).total_seconds(),
        trades,
    )

    return np.max(list(durations)) / (60 * 60 * 24)


def avg_trade_duration(trades: List[Trade]) -> int:
    """Calculate the duration of the longest trade."""
    durations = map(
        lambda trade: (trade.exit_date - trade.entry_date).total_seconds(),
        trades,
    )

    return np.mean(list(durations)) / (60 * 60 * 24)


def winning_trades(trades: List[Trade]) -> List[Trade]:
    return reduce(
        lambda accum, trade: [*accum, trade]
        if (trade.exit_price - trade.entry_price) * trade.direction > 0
        else accum,
        trades,
        []
    )


def losing_trades(trades: List[Trade]) -> List[Trade]:
    return reduce(
        lambda accum, trade: [*accum, trade]
        if (trade.exit_price - trade.entry_price) * trade.direction < 0
        else accum,
        trades,
        []
    )


def trades_net_profit_sum(trades: List[Trade]) -> float:
    return reduce(
        lambda accum, trade: accum + trade.units * (trade.exit_price - trade.entry_price) * trade.direction,
        trades,
        0
    )


def trades_net_profit(trades: List[Trade]) -> List[float]:
    return list(map(
        lambda trade: trade.units * (trade.exit_price - trade.entry_price) * trade.direction,
        trades,
    ))


def profit_factor(trades: List[Trade]) -> float:
    """Calculate the profit factor."""
    win_trades = winning_trades(trades)
    lose_trades = losing_trades(trades)

    if len(lose_trades) == 0:
        return np.inf
    else:
        return trades_net_profit_sum(win_trades) / np.abs(trades_net_profit_sum(lose_trades))


def expectancy_pct(trades: List[Trade]) -> float:
    """Calculate the expectancy percentage."""
    win_trades = winning_trades(trades)
    lose_trades = losing_trades(trades)
    if len(lose_trades) == 0:
        return np.mean(win_trades) * 100
    elif len(win_trades) == 0:
        return np.mean(lose_trades) * 100
    else:
        win_rate = win_rate_pct(trades)
        avg_win = avg_trade_pct(win_trades)
        avg_loss = avg_trade_pct(lose_trades)
        return (win_rate * avg_win - (1 - win_rate) * avg_loss) * 100


def sqn(trades):
    """Calculate the System Quality Number."""

    net_profit = trades_net_profit(trades)

    N = len(trades)
    avg = np.mean(net_profit)
    std = np.std(net_profit)

    return np.sqrt(N) * (avg / std)
