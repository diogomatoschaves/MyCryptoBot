import pandas as pd
from sqlalchemy import create_engine


def extract_data(
    asset='BTC',
    db_url='sqlite:///../database/db.sqlite3',
    table='model_lunarcrushtimeentries',
):

    engine = create_engine(db_url)
    df = pd.read_sql_table(table, engine, parse_dates=['time'], index_col='time')

    df = df[df["asset"] == asset].sort_values(by='time').copy()

    return df
