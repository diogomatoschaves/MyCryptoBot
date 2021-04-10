import shared.exchanges.binance.constants as const


def resample_data(data, candle_size, aggregation_method):
    return data \
        .resample(const.CANDLE_SIZES_MAPPER[candle_size]) \
        .agg(aggregation_method) \
        .ffill()

