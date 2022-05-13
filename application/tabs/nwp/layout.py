""" PV lyaout code """

import asyncio

import dash_bootstrap_components as dbc
import pandas as pd
import xarray as xr
from dash import dcc, html

from .download import download_data


async def nwp_make_layout():
    """Make pv htm layout"""

    await asyncio.sleep(0.1)

    download_data()

    nwp_xr = xr.load_dataset("nwp_latest.netcdf")["UKV"]

    variables = nwp_xr["variable"].values
    init_times = nwp_xr.init_time.values

    # do we need pandas for this?
    init_times = [pd.to_datetime(init_time).isoformat() for init_time in init_times]

    drop_downs = html.Div(
        [
            html.Div("Init time"),
            dcc.Dropdown(
                init_times,
                init_times[0],
                id="nwp-dropdown-init-time",
                style={"width": "100%"},
            ),
            html.Div("Variables"),
            dcc.Dropdown(
                variables,
                variables[0],
                id="nwp-dropdown-variables",
                style={"width": "100%"},
            ),
            html.Div(""),
            dbc.Button("Refresh", id="nwp-refresh"),
            dcc.Loading(
                id="nwp-refresh-status", type="default", children=html.Div(id="loading-output-1")
            ),
        ]
    )

    plot = (
        dcc.Graph(
            id="nwp-plot",
            # figure=make_pv_plot(),
            style={"width": "100%"},
        ),
    )

    tab2 = html.Div(
        [
            html.H3("NWP data (latest)"),
            dbc.Row(
                [
                    dbc.Col(html.Div(drop_downs), width=2),
                    dbc.Col(html.Div(plot)),
                ],
            ),
            dcc.Store(id="store-nwp-data", storage_type="memory"),
        ]
    )

    return tab2
