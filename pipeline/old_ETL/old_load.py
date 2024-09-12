"""Loads local data into redshift database."""

from datetime import datetime

import redshift_connector


def get_redshift_conn(conf):
    """Established connection to AWS redshift database."""
    return redshift_connector.connect(
        host=conf["DB_HOST"],
        database=conf["DB_NAME"],
        port=conf["DB_PORT"],
        user=conf["DB_USER"],
        password=conf["DB_PASSWORD"])


def is_valid_data(entry: list) -> bool:
    """Checks provided data list is valid."""
    truck_id, p_method, total, at = entry[0], entry[1], entry[2], entry[3]

    if not isinstance(truck_id, int) or not truck_id in range(7):
        return False

    if not isinstance(p_method, int) or not p_method in range(1, 3):
        return False

    if not isinstance(total, int) or not total in range(200001):
        return False

    if not isinstance(at, str):
        return False

    date_obj = None

    try:
        date_obj = datetime.strptime(at, "%Y-%m-%d")
    except ValueError:
        print("Invalid date detected.")

    if not date_obj or date_obj > datetime.now():
        return False

    return True


def check_data_to_upload(data: list[list]) -> list[list]:
    """Checks whether nested data list contains valid entries."""
    output_msg = ""
    output_list = []
    invalid_locs = []
    for i, entry in enumerate(data):
        if is_valid_data(entry):
            output_list.append(entry)

        else:
            invalid_locs.append(i)

    if not invalid_locs:
        output_msg = "Data valid and uploaded successfully."
    else:
        output_msg = f"Entries at locations: {
            invalid_locs} were not uploaded due to invalid data."

    return output_list, output_msg


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

    # print(f"\n---\n{check_msg}\n---")
