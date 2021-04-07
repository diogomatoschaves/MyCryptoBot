from data.transform.lunarcrush.cleaning import clean_df


def transform_data(df):

    # Data Cleaning
    df = clean_df(df)

    return df
