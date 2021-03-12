from data_processing.extract.extract import extract_data
from data_processing.load import load_data
from data_processing.transform import transform_data


def etl_pipeline(config):

    asset = 'BTC'

    df = extract_data(asset, db_url=config.database_dir, table=config.table)

    df = transform_data(df)

    load_data(df, config)

    return df
