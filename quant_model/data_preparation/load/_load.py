import os


def load_data(df, config, file_name='bitcoin_clean.csv'):

    file_path = os.path.join(config.data_dir_base, file_name)

    df.to_csv(file_path)
