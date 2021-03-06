"""Main plots function """
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import pandas as pd
from log import logger
from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.models.base import Base_PV
from nowcasting_datamodel.models.pv import PVSystemSQL, PVYield, PVYieldSQL
from nowcasting_datamodel.read.read_pv import get_pv_yield
from plotly import graph_objects as go


def get_all_pv_systems_ids() -> List[int]:
    """Get all pv systems ids from database"""
    # make database connection
    url = os.getenv("DB_URL_PV")
    assert url is not None, "DB_URL_PV has not been set"
    db_connection = DatabaseConnection(url=url, base=Base_PV)

    with db_connection.get_session() as session:
        pv_system_ids = session.query(PVSystemSQL.pv_system_id).all()

        pv_system_ids = [pv_system_id[0] for pv_system_id in pv_system_ids]

    return pv_system_ids


def make_pv_plot(pv_systems_ids: Optional[List[int]] = None, normalize: bool = False):
    """Make PV plot"""

    logger.info(f"Making PV plot for {pv_systems_ids=} and {normalize=}")

    # make database connection
    url = os.getenv("DB_URL_PV")
    db_connection = DatabaseConnection(url=url, base=Base_PV)

    if pv_systems_ids is None:
        pv_systems_ids = [10003, 10020, 10033, 10041, 10078, 10334, 10427, 10510, 10903, 11144]

    with db_connection.get_session() as session:
        start_utc = datetime.now(tz=timezone.utc) - timedelta(days=1)
        pv_yields: List[PVYieldSQL] = get_pv_yield(
            session=session, start_utc=start_utc, pv_systems_ids=pv_systems_ids
        )

        pv_yields = [PVYield.from_orm(pv_yield) for pv_yield in pv_yields]

    if normalize:
        # TODO move this to model
        logger.debug("Normalizing data")
        pv_yields_dict = []
        for pv_yield in pv_yields:
            solar_generation_normalized = (
                100 * pv_yield.solar_generation_kw / pv_yield.pv_system.installed_capacity_kw
            )
            pv_yield_dict = pv_yield.__dict__
            pv_yield_dict["solar_generation_normalized"] = solar_generation_normalized
            pv_yields_dict.append(pv_yield_dict)

        variable = "solar_generation_normalized"
    else:
        pv_yields_dict = [pv_yield.__dict__ for pv_yield in pv_yields]
        variable = "solar_generation_kw"

        logger.debug("Normalizing data: done")

    pv_yields_df = pd.DataFrame(pv_yields_dict)

    if len(pv_yields_df) == 0:
        logger.warning("Found no pv yields, this might cause an error")
        # this gives an empty plot back, but stops error on page
        return go.Figure()
    else:
        logger.debug(f"Found {len(pv_yields_df)} pv yields")

    # get the system id from 'pv_system_id=xxxx provider=.....'
    print(pv_yields_df.columns)
    print(pv_yields_df["pv_system"])
    pv_yields_df["pv_system_id"] = (
        pv_yields_df["pv_system"].astype(str).str.split(" ").str[0].str.split("=").str[-1]
    )

    # pivot on
    pv_yields_df = pv_yields_df[["datetime_utc", "pv_system_id", variable]]
    pv_yields_df.drop_duplicates(
        ["datetime_utc", "pv_system_id", variable], keep="last", inplace=True
    )
    pv_yields_df = pv_yields_df.pivot(index="datetime_utc", columns="pv_system_id", values=variable)

    print(pv_yields_df.columns)

    # plot
    traces_pv = []
    for i in range(len(pv_yields_df.columns)):
        trace_pv = go.Scatter(
            x=pv_yields_df.index,
            y=pv_yields_df[pv_yields_df.columns[i]],
            mode="lines+markers",
            name=pv_yields_df.columns[i],
        )
        traces_pv.append(trace_pv)

    fig = go.Figure(data=traces_pv)
    fig.update_layout(
        title="PV data",
        xaxis_title="Time [UTC]",
        yaxis_title="Solar generation [kW]",
    )

    if normalize:
        fig.update_layout(
            yaxis_title="Solar generation [%]",
        )

    return fig
