from datetime import timedelta

import humanfriendly

legend_mapping = {
    "accumulated_returns": "Buy & Hold",
    "accumulated_strategy_returns": "Strategy returns (no trading costs)",
    "accumulated_strategy_returns_tc": "Strategy returns (with trading costs)"
}
results_mapping = {
    'initial_equity': lambda unit: f"Initial Equity [{unit}]",
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
    'total_duration': "Total Duration",
    'start_date': "Start Date",
    'end_date': "End Date",
}
results_aesthetics = {
    'total_duration': lambda delta: humanfriendly.format_timespan(delta, max_units=2),
    'max_drawdown_duration': lambda delta: humanfriendly.format_timespan(delta, max_units=2),
    'avg_drawdown_duration': lambda sec: humanfriendly.format_timespan(sec, max_units=2),
    'max_trade_duration': lambda delta: humanfriendly.format_timespan(delta, max_units=2),
    'avg_trade_duration': lambda sec: humanfriendly.format_timespan(sec, max_units=2),
}

results_sections = {
    'Overview': ['total_duration', 'start_date', 'end_date', 'trading_costs',
                 'leverage', 'initial_equity', 'exposed_capital', 'exposure_time'],
    'Returns': ['return_pct', 'equity_final', 'equity_peak', 'return_pct_annualized',
                'volatility_pct_annualized', 'buy_and_hold_return', ],
    'Drawdowns': ['max_drawdown', 'avg_drawdown', 'max_drawdown_duration', 'avg_drawdown_duration'],
    'Trades': ['nr_trades', 'win_rate', 'best_trade', 'worst_trade', 'avg_trade',
               'max_trade_duration', 'avg_trade_duration'],
    'Ratios': ['sharpe_ratio', 'sortino_ratio', 'calmar_ratio', 'profit_factor', 'expectancy', 'sqn']
}