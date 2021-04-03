import numpy as np


def fill_null_values(df, columns):
    for col in columns:
        df[col] = np.where(df[col].isnull(), 0, df[col])

    return df


def interpolate_ffill_bfill_values(df, columns):
    for column in columns:
        df[column] = df.loc[:, [column]].interpolate(method='linear')

    df[columns] = df[columns].ffill().bfill()

    return df


def delete_null_columns(df):
    null_columns = df.columns[df.isnull().any(axis=0)]

    df = df.drop(columns=null_columns)

    return df


def clean_df(df):

    df = df.drop(columns=['search_average', 'social_contributors'])

    # Fill null values with 0
    columns = ["medium", "youtube", "url_shares", "unique_url_shares", "news", "reddit_posts", "reddit_posts_score"]

    df = fill_null_values(df, columns)

    # Interpolate, ffill and bfill null values on specific columns
    columns = ['volume_24h_rank', 'alt_rank', 'social_volume_global', 'social_dominance', 'market_dominance']

    df = interpolate_ffill_bfill_values(df, columns)

    # Delete null columns
    df = delete_null_columns(df)

    return df
