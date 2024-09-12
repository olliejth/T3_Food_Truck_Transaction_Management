from datetime import datetime, date, timedelta
import json
import pandas as pd
from html_writer import create_html_string


def get_payment_method_mapping(connection):
    """Creates dictionary that maps payment types to IDs."""
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM oliver_thompson_schema.DIM_Payment_Method;")

        result = cur.fetchall()

    mapping_dict = {}

    for item in result:
        mapping_dict[item[1]] = item[0]

    return mapping_dict


def export_to_json(report_data: dict):

    filepath = "./report_jsons"

    yesterday = date.today() - timedelta(days=1)
    filename = f"{filepath}/report_data_{yesterday}.json"

    with open(filename, "w", encoding='utf-8') as f_obj:
        json.dump(report_data, f_obj, indent=2)


def export_to_html(report_data: dict) -> None:

    html_content = create_html_string(report_data)

    filepath = "./report_htmls"

    yesterday = date.today() - timedelta(days=1)
    filename = f"{filepath}/report_data_{yesterday}.html"

    with open(filename, "w", encoding='utf-8') as f_obj:
        f_obj.write(html_content)


def get_yesterdays_data(connection) -> tuple[list]:
    today = date.today()
    yesterday = today - timedelta(days=1)

    q_string = """
    SELECT * FROM oliver_thompson_schema.fact_transaction
    WHERE DATE(at) = %s;"""

    with connection.cursor() as cur:
        cur.execute(q_string, (yesterday, ))

        data = cur.fetchall()

    return data


def fix_data(connection, db_data: tuple[list]) -> list[list]:
    db_list = list(db_data)

    type_mapping = get_payment_method_mapping(connection)
    rev_type_mapping = {value: key for key, value in type_mapping.items()}

    for entity in db_list:
        entity[2] = rev_type_mapping[entity[2]]
        entity[3] = entity[3] / 100

    return db_list


def yesterday_data_to_dataframe(connection) -> pd.DataFrame:

    data_tuple = get_yesterdays_data(connection)

    data_list = fix_data(connection, data_tuple)

    cols = ["transaction_id", "truck_id", "payment_type", "total", "at"]
    df = pd.DataFrame(data_list, columns=cols)

    return df


def get_result_dict_list(df: pd.DataFrame) -> dict:
    dict_data = df.to_dict()

    output_list = []
    for k in dict_data.keys():
        entity_dict = {k: list(dict_data[k].values())}
        output_list.append(entity_dict)

    col_headings = [list(col.keys())[0] for col in output_list]
    no_of_entries = len(list(dict_data[col_headings[0]].values()))

    final_dict_list = []
    for i in range(no_of_entries):
        entity_dict = {}
        for col in col_headings:
            entity_dict[col] = dict_data[col][i]
        final_dict_list.append(entity_dict)

    return final_dict_list


def get_total_transactions(df: pd.DataFrame) -> dict:
    total_transactions = int(df["transaction_id"].count())

    return total_transactions


def get_transactions_per_truck_dict(df: pd.DataFrame) -> pd.DataFrame:
    transactions_per_truck = df.groupby(df['truck_id']).count().sort_values(
        'total', ascending=False).drop(columns=['at', 'payment_type', 'transaction_id']).reset_index()

    transactions_per_truck_dict = get_result_dict_list(transactions_per_truck)

    return transactions_per_truck_dict


def get_total_val_per_truck_dict(df: pd.DataFrame) -> dict:
    total_transaction_value = df.groupby(df['truck_id'])["total"].sum(
    ).reset_index().sort_values('total', ascending=False).round(2)

    transaction_value_dict = get_result_dict_list(total_transaction_value)

    for entity in transaction_value_dict:
        entity["total"] = f"${entity["total"]}"

    return transaction_value_dict


def get_payment_type_dict(df: pd.DataFrame) -> dict:

    total_payment_methods = df["payment_type"].value_counts().reset_index()
    total_payment_methods["proportion"] = (
        (total_payment_methods["count"] / df["payment_type"].count()) * 100).round(2)

    payment_methods = get_result_dict_list(total_payment_methods)

    for method in payment_methods:
        method["proportion"] = f"{method["proportion"]}%"

    return payment_methods


def combine_dicts(tl_tns: list[dict], tns_per_truck: list[dict],
                  truck_values: list[dict], pay_methods: list[dict]
                  ) -> list[dict]:

    output_dict = {}
    output_dict["total daily transactions"] = tl_tns
    output_dict["daily transactions per truck"] = tns_per_truck
    output_dict["total earnings per truck"] = truck_values
    output_dict["pay method proportions"] = pay_methods

    return output_dict
