"""Loads local data into redshift database."""

import csv
from datetime import datetime, timedelta
from os import environ as ENV

from dotenv import load_dotenv
import redshift_connector


def get_redshift_conn(env):
    """Established connection to AWS redshift database."""
    return redshift_connector.connect(
        host=env["DB_HOST"],
        database=env["DB_NAME"],
        port=env["DB_PORT"],
        user=env["DB_USER"],
        password=env["DB_PASSWORD"])


def get_payment_method_mapping(connection):
    """Creates dictionary that maps payment types to IDs."""
    with connection.cursor() as cur:
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


def prepare_data_for_upload(connection) -> list:
    """Formats data into proper types for SQL upload."""

    truck_data_list = create_csv_list()
    payment_mapping = get_payment_method_mapping(connection)

    output_list = []

    for tn in truck_data_list:
        truck_id = int(tn[4])
        payment_id = payment_mapping.get(tn[2])
        total = int(float(tn[3])*100)
        at = datetime.strptime(
            tn[1], '%Y-%m-%d %H:%M:%S%z') + timedelta(hours=1)

        output_list.append([truck_id, payment_id, total, at])

    return output_list


def upload_transaction_data(t_data: list, connection) -> None:
    """Uploads transaction data to the database."""
    # t_data, check_msg = check_data_to_upload(t_data)

    query_str = """
                INSERT INTO 
                oliver_thompson_schema.FACT_Transaction 
                (truck_id, payment_method_id, total, at)
                VALUES 
                (%s, %s, %s, %s);
                """

    with connection.cursor() as cur:
        cur.executemany(query_str, t_data)

        connection.commit()


if __name__ == "__main__":

    load_dotenv()

    conn = get_redshift_conn(ENV)

    formatted_data = prepare_data_for_upload(conn)

    upload_transaction_data(formatted_data, conn)

    conn.close()
