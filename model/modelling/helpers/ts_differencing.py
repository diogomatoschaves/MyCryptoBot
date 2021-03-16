"""
Python code for fractional differencing of pandas time series
illustrating the concepts of the article "Preserving Memory in Stationary Time Series"
by Simon Kuttruf

While this code is dedicated to the public domain for use without permission, the author disclaims any liability in connection with the use of this code.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller


def get_weights(d, lags):
    # return the weights from the series expansion of the differencing operator
    # for real orders d and up to lags coefficients
    w = [1]
    for k in range(1, lags):
        w.append(-w[-1] * (d - k + 1) / k)
    w = np.array(w).reshape(-1, 1)

    print(w)

    return w


def plot_weights(d_range, lags, number_plots):
    weights = pd.DataFrame(np.zeros((lags, number_plots)))
    interval = np.linspace(d_range[0], d_range[1], number_plots)

    for i, diff_order in enumerate(interval):
        weights[i] = get_weights(diff_order, lags)

    weights.columns = [round(x, 2) for x in interval]

    fig = weights.plot()
    plt.legend(title='Order of differencing')
    plt.title('Lag coefficients for various orders of differencing')
    plt.xlabel('lag coefficients')
    #plt.grid(False)
    plt.show()


def ts_differencing(series, order, lag_cutoff):
    # return the time series resulting from (fractional) differencing
    # for real orders order up to lag_cutoff coefficients

    weights = get_weights(order, lag_cutoff)
    res = 0
    for k in range(lag_cutoff):
        res += weights[k] * series.shift(k).fillna(0)

    return res[lag_cutoff:]


def plot_memory_corr(result, series_name):

    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    color1 = 'xkcd:deep red'
    color2 = 'xkcd:cornflower blue'

    ax.plot(result.order, result['adf'], color=color1)
    ax.plot(result.order, result['5%'], color='xkcd:slate')
    ax2.plot(result.order, result['corr'], color=color2)
    ax.set_xlabel('order of differencing')
    ax.set_ylabel('adf', color=color1);
    ax.tick_params(axis='y', labelcolor=color1)
    ax2.set_ylabel('corr', color=color2);
    ax2.tick_params(axis='y', labelcolor=color2)
    plt.title('ADF test statistics and correlation for %s' % series_name)
    plt.show()


def memory_corr(series, d_range, number_plots, lag_cutoff, series_name):
    # return a data frame and plot comparing adf statistics and linear correlation
    # for numberPlots orders of differencing in the interval dRange up to a lag_cutoff coefficients

    interval = np.linspace(d_range[0], d_range[1], number_plots)
    result = pd.DataFrame(np.zeros((len(interval),4)))
    result.columns = ['order', 'adf', 'corr', '5%']
    result['order'] = interval
    for counter, order in enumerate(interval):
        seq_traf = ts_differencing(series, order, lag_cutoff)
        res = adfuller(seq_traf, maxlag=1, regression='c') #autolag='AIC'
        result.loc[counter, 'adf'] = res[0]
        result.loc[counter, '5%'] = res[4]['5%']
        result.loc[counter, 'corr'] = np.corrcoef(series[lag_cutoff:].fillna(0), seq_traf)[0, 1]

    plot_memory_corr(result, series_name)
    return result
