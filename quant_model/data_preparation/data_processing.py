from quant_model.data_preparation.extract import extract_data
from quant_model.data_preparation.load import load_data
from quant_model.data_preparation.transform import transform_data


def etl_pipeline(config):

    asset = 'BTC'

    df = extract_data(asset, db_url=config.database_dir, table=config.table)

    df = transform_data(df)

    load_data(df, config)

    return df
