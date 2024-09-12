"""Creates pandas datframe from csv file which is then cleaned and re-saved."""

import os

import pandas as pd


def get_parquet_names(path: str) -> list[str]:
    """Gets strings of the parquet files in the /data folder."""
    filenames = []

    for file in os.listdir(path):
        if file.endswith('.parquet'):
            filenames.append(file)

    filenames.sort()
    return filenames


def combine_transaction_data_files(filenames: list[str], filepath: str,
                                   new_filename: str) -> None:
    """Loads and combines relevant files from the data/ folder.
    Produces a single combined file in the data/ folder."""

    parquet_list = [pd.read_parquet(
        f'{filepath}/{name}') for name in filenames]

    no_of_files = range(0, len(parquet_list))
    for i in no_of_files:
        parquet_list[i]["truck_id"] = i+1
    ###### FIX THIS, DO FROM NAME NOT POSITION ######

    combined_parquets = pd.concat(parquet_list)
    combined_parquets.to_csv(
        f"{filepath}/{new_filename}")


def get_dataframe_from_csv(filename: str, filepath: str) -> pd.DataFrame:
    """Creates pandas dataframe from csv file."""
    dataframe = pd.read_csv(f'{filepath}/{filename}')

    return dataframe


def clean_data(df: pd.DataFrame, invalid_values: list[str]) -> pd.DataFrame:
    """Cleans to make it ready for database upload."""
    # Remove unneeded column
    df = df.drop(columns=["Unnamed: 0"])

    # Remove NaN total values
    df = df.dropna(subset=["total"])

    # Remove invalid 'total' values
    for val in invalid_values:
        df = df[df.total != val]

    # Convert datatypes

    df.total = df.total.astype(float)

    df['timestamp'] = pd.to_datetime(
        df['timestamp'], format="%Y-%m-%d %H:%M:%S")

    return df


def save_df_to_csv(df: pd.DataFrame, filename: str, filepath: str) -> None:
    """Saves cleaned pandas dataframe to local csv file."""
    df.to_csv(f"{filepath}/{filename}")
