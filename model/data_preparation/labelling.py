import pandas as pd


def get_volatility(prices, span=100, delta=pd.Timedelta(hours=1)):
    # 1. compute returns of the form p[t]/p[t-1] - 1
    # 1.1 find the timestamps of p[t-1] values
    df0 = prices.index.searchsorted(prices.index - delta)
    df0 = df0[df0 > 0]
    # 1.2 align timestamps of p[t-1] to timestamps of p[t]
    df0 = pd.Series(prices.index[df0-1], index=prices.index[prices.shape[0] - df0.shape[0]:])
    # 1.3 get values by timestamps, then compute returns
    df0 = prices.loc[df0.index] / prices.loc[df0.values].values - 1
    # 2. estimate rolling standard deviation
    df0 = df0.ewm(span=span).std()

    return df0


def get_horizons(prices, delta=pd.Timedelta(minutes=15)):
    t1 = prices.index.searchsorted(prices.index + delta)
    t1 = t1[t1 < prices.shape[0]]
    t1 = prices.index[t1]
    t1 = pd.Series(t1, index=prices.index[:t1.shape[0]])
    return t1


def get_touches(prices, events, factors=(1, 1)):
    '''
    events: pd dataframe with columns
      t1: timestamp of the next horizon
      threshold: unit height of top and bottom barriers
      side: the side of each bet
    factors: multipliers of the threshold to set the height of
             top/bottom barriers
    '''
    out = events[['t1']].copy(deep=True)
    if factors[0] > 0:
        thresh_uppr = factors[0] * events['threshold']
    else:
        thresh_uppr = pd.Series(index=events.index)  # no uppr thresh

    if factors[1] > 0:
        thresh_lwr = -factors[1] * events['threshold']
    else:
        thresh_lwr = pd.Series(index=events.index)  # no lwr thresh

    for loc, t1 in events['t1'].iteritems():
        df0 = prices[loc:t1]                              # path prices
        df0 = (df0 / prices[loc] - 1) * events.side[loc]  # path returns
        out.loc[loc, 'stop_loss'] = \
            df0[df0 < thresh_lwr[loc]].index.min()  # earliest stop loss
        out.loc[loc, 'take_profit'] = \
            df0[df0 > thresh_uppr[loc]].index.min()  # earliest take profit
    return out


def get_labels(touches):
    out = touches.copy(deep=True)
    # pandas df.min() ignores NaN values

    first_touch = touches[['stop_loss', 'take_profit']].min(axis=1)

    for loc, t in first_touch.iteritems():
        if pd.isnull(t):
            out.loc[loc, 'label'] = 0
        elif t == touches.loc[loc, 'stop_loss']:
            out.loc[loc, 'label'] = -1
        else:
            out.loc[loc, 'label'] = 1
    return out