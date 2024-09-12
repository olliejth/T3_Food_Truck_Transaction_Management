from os import environ as ENV
from dotenv import load_dotenv
import pandas as pd
import redshift_connector
from report_functions import yesterday_data_to_dataframe, get_transactions_per_truck_dict, get_total_transactions, get_total_val_per_truck_dict, get_payment_type_dict, combine_dicts
from html_writer import create_html_string


def get_redshift_conn(env):
    """Established connection to AWS redshift database."""
    return redshift_connector.connect(
        host=env["DB_HOST"],
        database=env["DB_NAME"],
        port=env["DB_PORT"],
        user=env["DB_USER"],
        password=env["DB_PASSWORD"])


def generate_report():
    load_dotenv()
    conn = get_redshift_conn(ENV)

    truck_df = yesterday_data_to_dataframe(conn)

    total_transactions = get_total_transactions(truck_df)

    tns_per_truck = get_transactions_per_truck_dict(truck_df)

    val_per_food_truck = get_total_val_per_truck_dict(truck_df)

    payment_methods = get_payment_type_dict(truck_df)

    full_report_dict = combine_dicts(total_transactions,
                                     tns_per_truck,
                                     val_per_food_truck,
                                     payment_methods)

    output_html = create_html_string(full_report_dict)

    conn.close()

    return output_html


if __name__ == "__main__":
    pass
