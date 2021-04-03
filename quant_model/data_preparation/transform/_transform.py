from quant_model.data_preparation.transform.cleaning import clean_df
from quant_model.data_preparation.transform.feature_engineering import engineer_features


def transform_data(df):

    # Data Cleaning
    df = clean_df(df)

    # Feature Engineering
    df = engineer_features(df)

    return df
