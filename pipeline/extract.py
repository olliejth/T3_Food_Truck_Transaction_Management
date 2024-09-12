"""Extracts and downloads truck data from an AWS S3 bucket."""

from os import environ as ENV
from datetime import datetime

from boto3 import client
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = ENV["BUCKET_NAME"]
DATA_FILEPATH = ENV["DATA_FILEPATH"]


def get_s3_client(config):
    """Returns boto3 s3 client."""
    return client(service_name="s3",
                  aws_access_key_id=config["AWS_ACCESS_KEY"],
                  aws_secret_access_key=config["AWS_PRIVATE_ACCESS_KEY"])


def get_bucket_names(s3_client) -> list[str]:
    """Returns all bucket names"""
    return [b["Name"] for b in s3_client.list_buckets()["Buckets"]]


def get_bucket_by_name(s3_client, bucket_name: str):
    """Returns a bucket given a specific name."""
    output_bucket = s3_client.list_objects(Bucket=bucket_name)
    return output_bucket


def is_valid_file(file_name: str) -> bool:
    """Filters the bucket files by naming convention and filetype."""
    if file_name.startswith("trucks/") and file_name.endswith(".csv"):
        return True
    return False


def is_recent_upload(file_name: str) -> bool:
    """Checks whether a file has been uploaded in the past three hours."""

    name_list = file_name.split("/")
    file_year = int(name_list[1].split("-")[0])
    file_month = int(name_list[1].split("-")[1])
    file_day = int(name_list[2])
    file_hour = int(name_list[3])

    now = datetime.now()

    if file_year != now.year or file_month != now.month or file_day != now.day:
        return False

    hours_since = datetime.now().hour - file_hour

    if all((hours_since < 3, hours_since >= 0)):
        return True
    return False


def download_truck_data_files(s3_client, target_bucket, config):
    """Downloads relevant files from S3 to a data/ folder."""
    for file in target_bucket["Contents"]:
        if is_valid_file(file["Key"]) and is_recent_upload(file["Key"]):
            new_filename = file["Key"].replace(
                "trucks/", "").replace("/", "-").replace("-T3_", "_")
            s3_client.download_file(f'{config["BUCKET_NAME"]}',
                                    file["Key"],
                                    f"{config["DATA_FILEPATH"]}/{new_filename}")


if __name__ == "__main__":

    s3 = get_s3_client(ENV)

    bucket = get_bucket_by_name(s3, BUCKET_NAME)

    download_truck_data_files(s3, bucket, ENV)
