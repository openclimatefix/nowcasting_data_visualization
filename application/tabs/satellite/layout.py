""" PV lyaout code """

import asyncio

import dash_bootstrap_components as dbc
import xarray as xr
from dash import dcc, html
from log import logger

from .download import download_satellite_data


async def satellite_make_layout():
    """Make pv htm layout"""

    try:

        await asyncio.sleep(0.1)

        download_satellite_data()

        with xr.open_dataset("zip::satellite_latest.zarr.zip", engine="zarr") as satellite_xr:
            variables = satellite_xr["variable"].values.tolist()

        drop_downs = html.Div(
            [
                html.Div("Variables"),
                dcc.Dropdown(
                    variables,
                    variables[0],
                    id="satellite-dropdown-variables",
                    style={"width": "100%"},
                ),
                html.Div(""),
                dbc.Button("Refresh", id="satellite-refresh"),
                dcc.Loading(
                    id="satellite-refresh-status",
                    type="default",
                    children=html.Div(id="loading-output-satellite"),
                ),
            ]
        )

        plot = (
            dcc.Graph(
                id="satellite-plot",
                # figure=make_pv_plot(),
                style={"width": "100%"},
            ),
        )

        tab2 = html.Div(
            [
                html.H3("satellite data (latest)"),
                dbc.Row(
                    [
                        dbc.Col(html.Div(drop_downs), width=2),
                        dbc.Col(html.Div(plot)),
                    ],
                ),
                dcc.Store(id="store-satellite-data", storage_type="memory"),
            ]
        )

    except Exception as e:
        logger.error(e)
        raise Exception("Could not make satellite page")

    return tab2
