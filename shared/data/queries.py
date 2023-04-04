import pandas as pd


def get_data(model_class, start_date, symbol, interval, exchange='binance'):

    query = dict(exchange=exchange, symbol=symbol, interval=interval)

    if start_date:
        query["open_time__gte"] = start_date

    rows = model_class.objects.filter(**query).order_by('open_time').values()

    data = pd.DataFrame(rows).set_index('open_time')

    return data
