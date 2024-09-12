"""T3 Food trucks full ETL pipeline."""

from datetime import datetime
import csv
from os import environ as ENV

from dotenv import load_dotenv
import redshift_connector

import pipeline.old_extract as E
import pipeline.old_ETL.old_transform as T
import pipeline.old_load as L


def get_redshift_conn(conf):
    """Established connection with redshift database."""
    return redshift_connector.connect(
        host=conf["DB_HOST"],
        database=conf["DB_NAME"],
        port=conf["DB_PORT"],
        user=conf["DB_USER"],
        password=conf["DB_PASSWORD"])


def get_payment_method_mapping(conn):
    """Creates dictionary that maps payment types to IDs."""
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM oliver_thompson_schema.DIM_Payment_Method;")

        result = cur.fetchall()

    mapping_dict = {}

    for item in result:
        mapping_dict[item[1]] = item[0]

    return mapping_dict


def create_csv_list() -> list:
    """Generates nested list from local csv."""
    csv_list = []
    with open("./data/clean_data.csv",
              "r", encoding="utf-8") as f_obj:
        file_reader = csv.reader(f_obj)

        next(file_reader)

        for row in file_reader:
            csv_list.append(row)

    return csv_list


def prepare_data_for_upload(conn) -> list:
    """Formats data into proper types for SQL upload."""

    truck_data_list = create_csv_list()
    payment_mapping = get_payment_method_mapping(conn)

    output_list = []

    for tn in truck_data_list:
        truck_id = int(tn[4])
        payment_id = payment_mapping.get(tn[2])
        total = int(float(tn[3])*100)
        at = datetime.strptime(tn[1], "%Y-%m-%d %H:%M:%S")

        output_list.append([truck_id, payment_id, total, at])

    return output_list


if __name__ == "__main__":

    load_dotenv()

# EXTRACT
    s3 = E.get_s3_client(ENV)

    s3_buckets = E.get_bucket_names(s3)

    truck_bucket = E.get_bucket_by_name(s3, ENV["BUCKET_NAME"])

    E.download_truck_data_files(s3, truck_bucket, ENV)

# TRANSFORM
    DATA_FILEPATH = ENV["DATA_FILEPATH"]

    parquet_name_list = T.get_parquet_names(DATA_FILEPATH)

    MERGED_FILENAME = ENV['MERGED_FILENAME']
    T.combine_transaction_data_files(parquet_name_list,
                                     DATA_FILEPATH,
                                     MERGED_FILENAME)

    trucks = T.get_dataframe_from_csv(MERGED_FILENAME, DATA_FILEPATH)

    error_vals = ["ERR", "0.00", "0", "VOID", "blank"]
    trucks = T.clean_data(trucks, error_vals)

    T.save_df_to_csv(trucks, "clean_data.csv", DATA_FILEPATH)

# LOAD
    session_connection = get_redshift_conn(ENV)

    formatted_data = prepare_data_for_upload(session_connection)

    L.upload_transaction_data(formatted_data, session_connection)

    session_connection.close()
