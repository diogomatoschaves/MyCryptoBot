import re

import pandas as pd
from django.db import connection


def get_query(model_class, start_date, symbol, interval, exchange='binance'):

    query = dict(exchange=f"'{exchange}'", symbol=f"'{symbol}'", interval=f"'{interval}'")

    if start_date:
        query["open_time__gte"] = start_date

    sql_query = str(model_class.objects.filter(**query).order_by('open_time').query)

    pattern = r"\d{4}-\d{2}-\d{2}\s*\d+:\d+:\d+[-+]\d+:\d+"
    sql_query = re.sub(pattern, r"'\g<0>'", sql_query)

    return sql_query


def get_data(model_class, start_date, symbol, interval, exchange='binance'):

    query = get_query(model_class, start_date, symbol, interval, exchange)

    data = pd.read_sql_query(query, connection, parse_dates=['open_time'], index_col='open_time')

    return data
