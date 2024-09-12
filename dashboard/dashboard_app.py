"""Code to configure and run streamlit visualisations."""

from os import environ as ENV

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from functions import get_redshift_conn, total_truck_transactions, average_transactions
from functions import transactions_by_date, transactions_by_weekday


if __name__ == "__main__":

    load_dotenv()
    conn = get_redshift_conn(ENV)

    with conn.cursor() as cur:
        cur.execute("select * from oliver_thompson_schema.fact_transaction;")

        db_data = cur.fetchall()

    conn.close()

    truck_df = pd.DataFrame(
        db_data, columns=['transaction_id', 'truck_id', 'type', 'total', 'timestamp'])

    total_transactions = total_truck_transactions(truck_df)

    avg_transactions = average_transactions(truck_df)

    transactions_over_time = transactions_by_date(truck_df)

    weekday_transactions = transactions_by_weekday(truck_df)

    st.sidebar.markdown("# Sidebar")
    st.sidebar.multiselect("Trucks", options=[1, 2, 3, 4, 5, 6])

    cols = st.columns(2)
    with cols[0]:
        st.altair_chart(total_transactions, use_container_width=True)
        st.altair_chart(avg_transactions, use_container_width=True)

    with cols[1]:
        st.altair_chart(transactions_over_time, use_container_width=True)
        st.altair_chart(weekday_transactions, use_container_width=True)
