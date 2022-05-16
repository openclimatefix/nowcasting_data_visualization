""" Callbacks functions """

from datetime import datetime, timezone

import pandas as pd
import xarray as xr
from dash import Input, Output
from log import logger

from .download import download_satellite_data
from .plots import plot_satellite_data


def satellite_make_callbacks(app):
    """Make callbacks"""

    @app.callback(
        Output("satellite-refresh-status", "children"), Input("satellite-refresh", "n_clicks")
    )
    def refresh_trigger(n_clicks):

        logger.debug(f"Downloading data {n_clicks=}")

        download_satellite_data(replace=True)

        now_text = datetime.now(timezone.utc).strftime("Refresh time: %Y-%m-%d %H:%M:%S  [UTC]")
        return f"Last refreshed at {now_text}"

    @app.callback(
        [
            Output("satellite-dropdown-variables", "options"),
        ],
        Input("satellite-refresh-status", "children"),
    )
    def make_satellite_drop_downs(refresh_time):

        logger.debug(f"Making satellite drop downs for {refresh_time=}")

        satellite_xr = xr.open_dataset("zip::satellite_latest.zarr.zip", engine="zarr")
        variables = satellite_xr["variable"].values

        logger.debug(f"Variables are {variables}")

        logger.debug(f"Making satellite drop downs for {refresh_time=}: done")

        return variables

    @app.callback(
        Output("satellite-plot", "figure"),
        [
            Input("satellite-dropdown-variables", "value"),
            Input("satellite-refresh-status", "children"),
        ],
    )
    def callback_make_satellite_plot(variable, refresh_time):

        logger.debug(f"Making plot for data refresh at {refresh_time=} {variable=}")

        fig = plot_satellite_data(variable)

        return fig

    return app
