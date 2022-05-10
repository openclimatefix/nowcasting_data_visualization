""" Callbacks functions """

from datetime import datetime, timezone

import pandas as pd
import xarray as xr
from dash import Input, Output
from log import logger

from .download import download_data
from .plots import plot_nwp_data


def nwp_make_callbacks(app):
    """Make callbacks"""

    @app.callback(Output("nwp-refresh-status", "children"), Input("nwp-refresh", "n_clicks"))
    def refresh_trigger(n_clicks):

        logger.debug(f"Downloading data {n_clicks=}")

        download_data(replace=True)

        now_text = datetime.now(timezone.utc).strftime("Refresh time: %Y-%m-%d %H:%M:%S  [UTC]")
        return f"Last refreshed at {now_text}"

    @app.callback(
        [Output("nwp-dropdown-init-time", "options"), Output("nwp-dropdown-variables", "options")],
        Input("nwp-refresh-status", "children"),
    )
    def make_nwp_drop_downs(refresh_time):

        logger.debug(f"Making nwp drop downs for {refresh_time=}")

        nwp_xr = xr.load_dataset("nwp_latest.netcdf")["UKV"]
        variables = nwp_xr["variable"].values
        init_times = nwp_xr.init_time.values

        init_times = [pd.to_datetime(init_time).isoformat() for init_time in init_times]

        logger.debug(f"Variables are {variables}")
        logger.debug(f"init_times are {init_times}")

        return init_times, variables

    @app.callback(
        Output("nwp-plot", "figure"),
        [
            Input("nwp-dropdown-init-time", "value"),
            Input("nwp-dropdown-variables", "value"),
            Input("nwp-refresh-status", "children"),
        ],
    )
    def callback_make_nwp_plot(init_time, variable, refresh_time):

        logger.debug(f"Making plot for data refresh at {refresh_time}")

        fig = plot_nwp_data(init_time, variable)

        return fig

    return app
