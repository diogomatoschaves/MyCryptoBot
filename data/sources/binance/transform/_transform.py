import logging

import numpy as np
import pandas as pd

import shared.exchanges.binance.constants as const


def add_extra_columns(data, exchange, symbol, candle_size):

    data[["exchange_id", "symbol_id", "interval"]] = [exchange, symbol, candle_size]

    return data


def remove_columns(data, columns=('id',)):
    try:
        data = data.drop(columns=columns)
    except KeyError:
        pass

    return data


def resample_data(data, candle_size, aggregation_method):
    return data \
        .resample(const.CANDLE_SIZES_MAPPER[candle_size]) \
        .agg(aggregation_method)


def remove_zeros(data):
    return data.replace(0, np.nan)


def set_index(data, index='open_time'):
    try:
        data = data.set_index(index)
    except KeyError:
        pass

    return data


def replace_nat_values(data):
    return data.fillna(np.nan)


def remove_incomplete_rows(data, resampled_data, candle_size, reference_candle_size, header=''):

    counts = data.resample(const.CANDLE_SIZES_MAPPER[candle_size]).count()

    rows = counts[(counts != const.COUNT_MAPPER[candle_size][reference_candle_size]).any(axis=1)].min(axis=1)

    logging.debug(header + f"Removed {len(rows)} from resampled data.")

    return resampled_data.drop(rows.index)


def transform_data(
    data,
    candle_size,
    exchange,
    symbol,
    reference_candle_size='5m',
    aggregation_method=const.COLUMNS_AGGREGATION,
    is_removing_zeros=False,
    is_removing_rows=False,
    header=''
):
    logging.debug(f'Transforming data with {data.shape[0]} rows and {data.shape[1]} columns.')

    data = remove_columns(data, ['id'])

    data = set_index(data, "open_time")

    if is_removing_zeros:
        data = remove_zeros(data)

    resampled_data = resample_data(data, candle_size, aggregation_method)

    if is_removing_rows:
        resampled_data = remove_incomplete_rows(data, resampled_data, candle_size, reference_candle_size, header=header)

    data = add_extra_columns(resampled_data, exchange, symbol, candle_size)

    return data
