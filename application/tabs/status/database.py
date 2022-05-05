"""Database functions for status """
import os
from datetime import datetime, timedelta, timezone

import humanize
import pandas as pd
from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.models.base import Base_PV
from nowcasting_datamodel.models.models import InputDataLastUpdated
from nowcasting_datamodel.read.read import (
    get_latest_forecast_created_utc,
    get_latest_input_data_last_updated,
)

pv_status = {"warning": timedelta(minutes=10), "error": timedelta(minutes=20)}
gsp_status = {"warning": timedelta(minutes=30), "error": timedelta(days=1)}
satellite_status = {"warning": timedelta(minutes=5), "error": timedelta(minutes=30)}
nwp_status = {"warning": timedelta(hours=1), "error": timedelta(hours=2)}

forecast_status = {"warning": timedelta(minutes=5), "error": timedelta(minutes=15)}

warnings_and_errors = pd.DataFrame(
    columns=["Consumer", "Warning", "Error"],
    data=[
        ["pv"] + list(pv_status.values()),
        ["gsp"] + list(gsp_status.values()),
        ["satellite"] + list(satellite_status.values()),
        ["nwp"] + list(nwp_status.values()),
    ],
)

warnings_and_errors_forecast = pd.DataFrame(
    columns=["Forecast", "Warning", "Error"],
    data=[
        ["national"] + list(forecast_status.values()),
        ["gsp"] + list(forecast_status.values()),
    ],
)


def get_forecast_status() -> dict:
    """Get forecast status"""
    url = os.getenv("DB_URL")
    assert url is not None, "DB_URL has not been set"
    db_connection = DatabaseConnection(url=url, base=Base_PV)

    with db_connection.get_session() as session:

        created_utc_national = get_latest_forecast_created_utc(session=session, gsp_id=0)
        # just check one gsp
        created_utc_gsp = get_latest_forecast_created_utc(session=session, gsp_id=1)

        forecast_df = pd.DataFrame(
            columns=["Forecast", "Last ran"],
            data=[
                ["national", created_utc_national],
                ["gsp", created_utc_gsp],
            ],
        )

        forecast_df = forecast_df.merge(warnings_and_errors_forecast)
        forecast_df = make_warnings_and_errors(
            data_df=forecast_df, check_column="Last ran", index_column="Forecast"
        )

    return forecast_df.to_dict("records")


def get_consumer_status() -> dict:
    """Get consumer status"""
    url = os.getenv("DB_URL")
    assert url is not None, "DB_URL has not been set"
    db_connection = DatabaseConnection(url=url, base=Base_PV)

    with db_connection.get_session() as session:
        input_data_last_updated = get_latest_input_data_last_updated(session=session)
        input_data_last_updated = InputDataLastUpdated.from_orm(input_data_last_updated)

    input_data_last_updated_df = pd.DataFrame(
        input_data_last_updated.__dict__.items(), columns=["Consumer", "Last pulled"]
    )

    input_data_last_updated_df = input_data_last_updated_df.merge(warnings_and_errors)
    input_data_last_updated_df = make_warnings_and_errors(input_data_last_updated_df)

    return input_data_last_updated_df.to_dict("records")


def make_warnings_and_errors(
    data_df, check_column: str = "Last pulled", index_column: str = "Consumer"
) -> pd.DataFrame:
    """
    Check "Last Pulled" columns agains warning and error column

    :param data_df: dataframe containing
        - Last pulled
        - Warning
        - Error
    :param check_column: the column that has the datetime we should check
    :param index_column: the index columns
    :return: Dataframe with 'Status' added to it
    """
    now = datetime.now(timezone.utc)
    index_warning = data_df[check_column] + data_df["Warning"] <= now
    index_error = data_df[check_column] + data_df["Error"] <= now

    # make status
    data_df["Status"] = "Ok"
    data_df.loc[index_warning, "Status"] = "Warning"
    data_df.loc[index_error, "Status"] = "Error"

    # re order
    data_df = data_df[[index_column, check_column, "Status", "Warning", "Error"]]

    # format
    data_df[check_column] = pd.to_datetime(data_df[check_column]).dt.strftime("%Y-%m-%d %H:%M:%S")
    data_df.rename(columns={check_column: f"{check_column} [UTC]"}, inplace=True)
    for col in ["Warning", "Error"]:
        data_df[col] = data_df[col].apply(lambda x: humanize.precisedelta(x))

    return data_df
