"""Creates pandas datframe from csv file which is then cleaned and re-saved."""

from os import listdir, remove
from os import environ as ENV
from datetime import datetime
import pytz

from dotenv import load_dotenv
import pandas as pd


def get_file_names(path: str, merged_file: str, clean_file: str) -> list[str]:
    """Gets strings of the parquet files in the /data folder."""
    filenames = []

    for file in listdir(path):
        if file.endswith('.csv') and file != merged_file and file != clean_file:
            filenames.append(file)

    return filenames


def combine_transaction_data_files(env) -> None:
    """Loads and combines relevant files from the data/ folder.
    Produces a single combined file in the data/ folder."""

    filepath = env["DATA_FILEPATH"]
    new_filename = env["MERGED_FILE"]
    filenames = get_file_names(
        env["DATA_FILEPATH"], env["MERGED_FILE"], env["CLEAN_FILE"])

    df_list = []
    for name in filenames:
        truck_id = int(name.split("_")[1][1])
        df = pd.read_csv(f'{filepath}/{name}')
        df["truck_id"] = truck_id
        df_list.append(df)

    combined_parquets = pd.concat(df_list)
    combined_parquets.to_csv(f"{filepath}/{new_filename}")


def get_dataframe_from_csv(filename: str, filepath: str) -> pd.DataFrame:
    """Creates pandas dataframe from csv file."""
    dataframe = pd.read_csv(f'{filepath}/{filename}')

    return dataframe


def delete_files(env, filenames: list[str]) -> None:
    """Deletes files in a given location."""
    for name in filenames:
        if name != env["CLEAN_FILE"]:
            remove(f"{env["DATA_FILEPATH"]}/{name}")


def save_df_to_csv(df: pd.DataFrame, filename: str, filepath: str) -> None:
    """Saves cleaned pandas dataframe to local csv file."""
    df.to_csv(f"{filepath}/{filename}")


def clean_data(env) -> None:
    """Cleans to make it ready for database upload."""

    df = get_dataframe_from_csv(env["MERGED_FILE"], env["DATA_FILEPATH"])

    # Remove unneeded column
    df = df.drop(columns=["Unnamed: 0"])

    # Remove NaN total values
    df = df.dropna(subset=["total"])

    # Remove invalid 'total' values
    for val in env["INVALID_TOTALS"].split(","):
        df = df[df["total"] != val]

    # Convert datatypes
    df["total"] = df["total"].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Eliminate extreme totals
    df = df[df["total"] < 250]
    df = df[df["total"] > 0]

    # Eliminate future times
    # Adjust based on your specific timezone
    timezone = pytz.timezone('Europe/London')
    now = timezone.localize(datetime.now())
    df = df[df["timestamp"] < now]

    # Eliminate invalid truck IDs
    df = df[df["truck_id"] > 0]
    df = df[df["truck_id"] < 7]

    files_to_delete = list(listdir(env['DATA_FILEPATH']))

    save_df_to_csv(df, env["CLEAN_FILE"], env["DATA_FILEPATH"])

    delete_files(env, files_to_delete)


if __name__ == "__main__":

    load_dotenv()

    combine_transaction_data_files(ENV)

    clean_data(ENV)
