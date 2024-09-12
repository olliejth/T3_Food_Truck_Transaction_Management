"""Functions for streamlit dashboard script."""

import pandas as pd
import altair as alt

import redshift_connector


def get_redshift_conn(conf):
    """Established connection with redshift database."""
    return redshift_connector.connect(
        host=conf["DB_HOST"],
        database=conf["DB_NAME"],
        port=conf["DB_PORT"],
        user=conf["DB_USER"],
        password=conf["DB_PASSWORD"])


def clean_data(df: pd.DataFrame, invalid_values: list[str]) -> pd.DataFrame:
    """Cleans to make it ready for database upload."""
    # Remove unneeded column
    df = df.drop(columns=["Unnamed: 0"])

    # Remove NaN total values
    df = df.dropna(subset=["total"])

    # Remove invalid 'total' values
    for val in invalid_values:
        df = df[df.total != val]

    # Convert datatypes
    df.total = df.total.astype(float)

    df['timestamp'] = pd.to_datetime(
        df['timestamp'], format="%Y-%m-%d %H:%M:%S")

    return df


def total_truck_transactions(df: pd.DataFrame) -> alt.Chart:
    """Creates altair bar chart of total transactions per food truck."""
    t_per_truck = df.groupby(df['truck_id'])
    format_data = t_per_truck.count().sort_values('total', ascending=False).drop(
        columns=['timestamp', 'type']).reset_index()

    chart = alt.Chart(format_data).mark_bar().encode(
        x=alt.X("truck_id:N", title=None),
        y=alt.Y("total", title="Total transactions"),
        color=alt.Color("truck_id:N", title="Truck ID")
    ).properties(title="Total transactions per food truck")

    return chart


def average_transactions(df: pd.DataFrame) -> alt.Chart:
    """Creates altair bar chart of average transaction amount per food truck."""
    avg_val_per_truck = df.groupby(df['truck_id'])[
        "total"].mean().reset_index().round(2)
    format_data = avg_val_per_truck.reset_index().round(2)

    chart = alt.Chart(format_data).mark_bar().encode(
        x=alt.X("truck_id:N", title=None),
        y=alt.Y("total", title="Average transaction cost (¢)"),
        color=alt.Color("truck_id:N", title="Truck ID")
    ).properties(title="Average transaction cost per truck ($)")

    return chart


def transactions_by_date(df: pd.DataFrame) -> alt.Chart:
    """Creates altair line graph of transaction frequency over time."""
    df["Date"] = df['timestamp'].dt.date

    trans_by_date = df.groupby(df['Date'])[
        'Date'].value_counts().reset_index()

    chart = alt.Chart(trans_by_date).mark_line().encode(
        x='Date:T',
        y=alt.Y('count:Q', title="Number of transactions")
    )

    return chart


def transactions_by_weekday(df: pd.DataFrame) -> alt.Chart:
    """Creates altair bar chart of transaction frequency per day of the week."""
    df["d_of_wk"] = [date_time.weekday() for date_time in df['timestamp']]

    by_day = df.groupby(df['d_of_wk'])[
        'd_of_wk'].value_counts().reset_index()

    day_mapping = {0: "Monday", 1: "Tuesday", 2: "Wednesday",
                   3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

    by_day["Weekday"] = [day_mapping[num]for num in by_day['d_of_wk']]

    days_of_week = ['Monday', 'Tuesday', 'Wednesday',
                    'Thursday', 'Friday', 'Saturday', 'Sunday']

    by_day['Weekday'] = pd.Categorical(
        by_day['Weekday'], categories=days_of_week, ordered=True)

    chart = alt.Chart(by_day).mark_bar().encode(
        x=alt.X("Weekday:N", sort=days_of_week, title=None),
        y=alt.Y("count:Q", title="Transactions per day"),
        color=alt.Color("Weekday:N", sort=days_of_week)
    ).properties(title="Total transactions per day of the week.").configure_range(
        category={'scheme': 'dark2'})

    return chart
