from datetime import timedelta

import humanfriendly

legend_mapping = {
    "accumulated_returns": "Buy & Hold",
    "accumulated_strategy_returns": "Strategy returns (no trading costs)",
    "accumulated_strategy_returns_tc": "Strategy returns (with trading costs)"
}
results_mapping = {
    'initial_equity': lambda unit: f"Initial Capital [{unit}]",
    'exposed_capital': lambda unit: f"Exposed Capital [{unit}]",
    'equity_final': lambda unit: f"Equity Final [{unit}]",
    'equity_peak': lambda unit: f"Equity Peak [{unit}]",
    'trading_costs': "Trading Costs [%]",
    'leverage': "Leverage [x]",
    'buy_and_hold_return': "Buy & Hold Return [%]",
    'exposure_time': "Exposure Time [%]",
    'return_pct': "Total Return [%]",
    'return_pct_annualized': "Annualized Return [%]",
    'volatility_pct_annualized': "Annualized Volatility [%]",
    'sharpe_ratio': "Sharpe Ratio",
    'sortino_ratio': "Sortino Ratio",
    'calmar_ratio': "Calmar Ratio",
    'max_drawdown': "Max Drawdown [%]",
    'avg_drawdown': "Avg Drawdown [%]",
    'max_drawdown_duration': "Max Drawdown Duration",
    'avg_drawdown_duration': "Avg Drawdown Duration",
    'nr_trades': "Total Trades",
    'win_rate': "Win Rate [%]",
    'best_trade': "Best Trade [%]",
    'worst_trade': "Worst Trade [%]",
    'avg_trade': "Avg Trade [%]",
    'max_trade_duration': "Max Trade Duration",
    'avg_trade_duration': "Avg Trade Duration",
    'profit_factor': "Profit Factor",
    'expectancy': "Expectancy [%]",
    'sqn': "System Quality Number",
}
results_aesthetics = {
    'total_duration': lambda delta: f"\tTotal Duration: {humanfriendly.format_timespan(delta)}",
    'start_date': lambda delta: f"\tStart Date: {delta}",
    'end_date': lambda delta: f"\tEnd Date: {delta}",
    'max_drawdown_duration': lambda delta: f"\tMax Drawdown Duration: {humanfriendly.format_timespan(delta)}",
    'avg_drawdown_duration': lambda sec: f"\tAvg Drawdown Duration: {humanfriendly.format_timespan(timedelta(seconds=sec))}",
    'max_trade_duration': lambda delta: f"\tMax Trade Duration: {humanfriendly.format_timespan(delta)}",
    'avg_trade_duration': lambda sec: f"\tAvg Trade Duration: {humanfriendly.format_timespan(timedelta(seconds=sec))}",
}
