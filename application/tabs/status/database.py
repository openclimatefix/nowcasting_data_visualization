"""Database functions for status """
import logging
import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import humanize
from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.models.base import Base_PV
from nowcasting_datamodel.models.models import InputDataLastUpdatedSQL, InputDataLastUpdated
from nowcasting_datamodel.read.read import get_latest_input_data_last_updated

logger = logging.getLogger(__name__)


pv_status = {"warning": timedelta(minutes=5), "error": timedelta(minutes=10)}

gsp_status = {"warning": timedelta(minutes=30), "error": timedelta(days=1)}

satellite_status = {"warning": timedelta(minutes=5), "error": timedelta(minutes=30)}

nwp_status = {"warning": timedelta(hours=1), "error": timedelta(hours=2)}

warnings_and_errors = pd.DataFrame(
    columns=["Consumer", "Warning", "Error"],
    data=[
        ["pv"] + list(pv_status.values()),
        ["gsp"] + list(gsp_status.values()),
        ["satellite"] + list(satellite_status.values()),
        ["nwp"] + list(nwp_status.values()),
    ],
)


def get_consumer_status() -> dict:
    """ Get consumer status """
    url = os.getenv("DB_URL")
    assert url is not None, "DB_URL has not been set"
    db_connection = DatabaseConnection(url=url, base=Base_PV)

    with db_connection.get_session() as session:
        input_data_last_updated = get_latest_input_data_last_updated(session=session)
        input_data_last_updated = InputDataLastUpdated.from_orm(input_data_last_updated)

    print(input_data_last_updated.__dict__)
    input_data_last_updated_df = pd.DataFrame(
        input_data_last_updated.__dict__.items(), columns=["Consumer", "Last pulled"]
    )

    now = datetime.now(timezone.utc)
    print(input_data_last_updated_df)
    print(warnings_and_errors)
    input_data_last_updated_df = input_data_last_updated_df.merge(warnings_and_errors)

    index_warning = (
        input_data_last_updated_df["Last pulled"] + input_data_last_updated_df["Warning"] <= now
    )
    index_error = (
        input_data_last_updated_df["Last pulled"] + input_data_last_updated_df["Error"] <= now
    )

    # make status
    input_data_last_updated_df["Status"] = "Ok"
    input_data_last_updated_df.loc[index_warning, "Status"] = "Warning"
    input_data_last_updated_df.loc[index_error, "Status"] = "Error"

    # re order
    input_data_last_updated_df = input_data_last_updated_df[
        ["Consumer", "Last pulled", "Status", "Warning", "Error"]
    ]

    # format
    input_data_last_updated_df["Last pulled"] = pd.to_datetime(
        input_data_last_updated_df["Last pulled"]
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
    input_data_last_updated_df.rename(columns={"Last pulled": "Last pulled [UTC]"}, inplace=True)
    for col in ['Warning','Error']:
        input_data_last_updated_df[col] = input_data_last_updated_df[col].apply(
            lambda x: humanize.precisedelta(x)
        )

    return input_data_last_updated_df.to_dict("records")
