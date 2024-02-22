import os
from datetime import datetime

import pandas as pd
import progressbar
import pytz

import shared.exchanges.binance.constants as const
from shared.data.queries import get_data
from shared.utils.helpers import get_root_dir
from data.sources.binance.extract._helpers import get_number_of_batches, get_end_date


def get_historical_data(
    symbol,
    candle_size,
    start_date,
    end_date=None,
    batch_size=1000,
    save_file=False,
    directory='database/datasets'
):
    """
    Fetches historical market data for a specified symbol from Binance, with the option to
    save the data to a CSV file.

    Parameters
    ----------
    symbol : str
        The ticker symbol for the cryptocurrency pair (e.g., "BTCUSDT").
    candle_size : str
        The size of the candles for the historical data (e.g., "1m", "1h").
    start_date : str or datetime
        The start date for the data retrieval in 'YYYY-MM-DD' format or as a datetime object.
    end_date : str, datetime, or None, optional
        The end date for the data retrieval in 'YYYY-MM-DD' format or as a datetime object.
         If None (default), uses the current date and time.
    batch_size : int, optional
        The number of candles to fetch per batch. Default is 1000.
    save_file : bool, optional
        If True, saves the fetched data to a CSV file. Default is False.
    directory : str, optional
        The directory where the CSV file will be saved, relative to the root directory. Default is 'data/'.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the historical market data indexed by 'open_time'. The DataFrame
        contains columns for open, high, low, close prices, and volume.

    Raises
    ------
    ValueError
        If the symbol or candle_size is not supported by the Binance API.

    Notes
    -----
    - This function utilizes the BinanceHandler class for fetching data from Binance.
        Ensure the class is properly configured to access the Binance API.
    - The progress of the data fetching process is displayed using a progress bar.

    Examples
    --------
    >>> data = get_historical_data("BTCUSDT", "1h", "2021-01-01", "2021-01-31")
    >>> print(data.head())

    Side Effects
    ------------
    - If `save_file` is True, this function writes a CSV file to disk in the specified `directory`.
    """

    if end_date is None:
        end_date = datetime.now(tz=pytz.utc)
    else:
        end_date = pd.Timestamp(end_date, tzinfo=pytz.utc)

    start_date = pd.Timestamp(start_date, tzinfo=pytz.utc)
    batch_start_date = start_date

    from shared.exchanges.binance import BinanceHandler

    binance_handler = BinanceHandler()

    data = pd.DataFrame()

    iterations = get_number_of_batches(start_date, candle_size, batch_size, end_date=end_date) + 1

    with progressbar.ProgressBar(max_value=iterations, redirect_stdout=True) as bar:
        i = 0
        end_reached = False
        while not end_reached:
            batch_data = extract_data(
                binance_handler.get_historical_klines,
                symbol,
                candle_size,
                start_date=batch_start_date,
                end_date=end_date,
                klines_batch_size=batch_size
            )

            data = pd.concat([data, batch_data], axis=0).drop_duplicates(["open_time"])

            batch_start_date = get_end_date(batch_start_date, candle_size, batch_size)

            end_reached = batch_start_date > end_date

            bar.update(i)
            i += 1

    if save_file:

        filepath = os.path.abspath(
            os.path.join(
                get_root_dir(),
                directory,
                '-'.join([
                    symbol,
                    candle_size,
                    start_date.replace(tzinfo=None).isoformat(timespec='minutes'),
                    end_date.replace(tzinfo=None).isoformat(timespec='minutes'),
                ]) + '.csv',
            )
        )

        data.to_csv(filepath)

    return data.set_index('open_time')


def extract_data(
    get_klines_method,
    symbol,
    candle_size,
    start_date,
    end_date=None,
    klines_batch_size=1000,
):
    """
    Fetches missing data on specified model class and for a
    specific symbol, candle_size and exchange from the Binance API.

    Parameters
    ----------
    get_klines_method: method - required. Historical data fetching function.
    symbol: str - required. Symbol for which to retrieve data.
    candle_size: str - optional. Candle size at which data should be retrieved.
    start_date: datetime object. Start date from which to retrieve data.
    end_date: datetime object - optional. If not specified, data will be fetched until last possible date
    klines_batch_size: int - optional. batch size of klines to retrieve on each function call.

    Returns
    -------
    DataFrame with fetched data.

    """
    batch_end_date = get_end_date(start_date, candle_size, klines_batch_size)

    if end_date is not None and batch_end_date > end_date:
        batch_end_date = end_date

    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int(batch_end_date.timestamp() * 1000)

    klines = get_klines_method(symbol, candle_size, start_timestamp, end_timestamp, limit=klines_batch_size)

    data = []
    for kline in klines:

        fields = {field: get_value(kline) for field, get_value in const.BINANCE_KEY.items()}

        data.append(fields)

    return pd.DataFrame(data)


def extract_data_db(exchange_data_model, symbol, base_candle_size, start_date):
    """
    Extracts data from a database for a given financial instrument.

    Parameters:
    - exchange_data (pd.DataFrame): DataFrame containing exchange data.
    - symbol (str): The symbol of the financial instrument.
    - candle_size (str): The size of the candles for the extracted data.
    - base_candle_size (str): The base size of candles for data retrieval.

    Returns:
    pd.DataFrame: A DataFrame containing the extracted data with the index reset.

    Example:
    >>> extract_data_db(exchange_data_model, 'BTCUSDT', '5m', '2020-01-01')
    # Returns a DataFrame with extracted data for BTC/USDT using 1-hour candles,
    # starting from the last available data point with 1-day candles.
    """

    data = get_data(exchange_data_model, start_date, symbol, base_candle_size, exchange='binance')
    return data.reset_index()
