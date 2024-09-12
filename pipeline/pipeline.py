"""Full pipeline script for batch upload of T3 transaction data."""

from os import environ as ENV

from dotenv import load_dotenv

from extract import get_s3_client, get_bucket_by_name, download_truck_data_files
from transform import combine_transaction_data_files, clean_data
from load import get_redshift_conn, prepare_data_for_upload, upload_transaction_data

if __name__ == "__main__":

    load_dotenv()

    # EXTRACT
    s3 = get_s3_client(ENV)

    bucket = get_bucket_by_name(s3, ENV["BUCKET_NAME"])

    download_truck_data_files(s3, bucket, ENV)

    # TRANSFORM
    combine_transaction_data_files(ENV)

    clean_data(ENV)

    # LOAD
    conn = get_redshift_conn(ENV)

    formatted_data = prepare_data_for_upload(conn)

    upload_transaction_data(formatted_data, conn)

    conn.close()
