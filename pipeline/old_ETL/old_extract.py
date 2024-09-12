"""Extracts and downloads truck data from an AWS S3 bucket."""

from boto3 import client


def get_s3_client(config):
    """Returns boto3 s3 client."""
    return client(service_name="s3",
                  aws_access_key_id=config["AWS_ACCESS_KEY"],
                  aws_secret_access_key=config["AWS_PRIVATE_ACCESS_KEY"])


def get_bucket_names(s3_client) -> list[str]:
    """Returns all bucket names"""
    return [b["Name"] for b in s3_client.list_buckets()["Buckets"]]


def get_bucket_by_name(s3_client, bucket_name: str):
    """Returns a bucket given a specfic name."""
    bucket = s3_client.list_objects(Bucket=bucket_name)
    return bucket


def is_valid_file(file_name: str) -> bool:
    """Filters the bucket files by naming convention and filetype."""
    if file_name.startswith("historical/TRUCK_DATA_HIST") and file_name.endswith(".parquet"):
        return True
    if file_name.startswith("metadata/details") and file_name.endswith(".xlsx"):
        return True
    return False


def download_truck_data_files(s3_client, bucket, config):
    """Downloads relevant files from S3 to a data/ folder."""
    for file in bucket["Contents"]:
        if is_valid_file(file["Key"]):
            new_filename = file["Key"].replace(
                "historical/", "").replace("metadata/", "")
            s3_client.download_file(f'{config["BUCKET_NAME"]}', file["Key"],
                                    f"./data/{new_filename}")
