""" Make summary layout """
import asyncio
import os

import dash_bootstrap_components as dbc
from dash import dcc, html

from .plots import get_gsp_boundaries, make_map_plot, make_plots


async def make_layout():
    """Make Summary layout"""

    await asyncio.sleep(0.1)

    boundaries = get_gsp_boundaries()

    modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader("GSP plot"),
                    dbc.ModalBody(
                        [
                            html.H4(id="hover_info"),
                            dcc.Graph(
                                id="plot-modal", figure=make_plots(gsp_id=1, show_yesterday=False)
                            ),
                        ]
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close", className="ml-auto")),
                    dcc.Store(id="store-gsp", storage_type="memory"),
                ],
                id="modal",
                is_open=False,
            ),
        ]
    )

    national_plot = html.Div(
        [
            dbc.Button("Refresh", id="summary-refresh"),
            dcc.Loading(
                id="summary-refresh-status",
                type="default",
                children=html.Div(id="summary-loading-output-1"),
            ),
            dcc.Interval(id="summary-interval", interval=1000 * 60 * 5),
            dcc.Checklist(["Yesterday"], [""], id="tick-show-yesterday"),
            dcc.Graph(
                id="plot-national",
            ),
            # html.Iframe(src='./uk_map.html')
        ],
        style={"width": "95%"},
    )

    national_map = html.Div(
        [
            dcc.Graph(
                id="plot-map",
            ),
            dcc.Interval(
                id="summary-slider-update",
                interval=int(os.getenv("MAP_REFRESH_SECONDS", "3")) * 1000,
            ),
            modal,
        ],
        style={"width": "95%"},
    )

    tab1 = html.Div(
        children=[
            dcc.RadioItems(
                id="radio-summary-normalize",
                options=[
                    {"label": "MW", "value": "0"},
                    {"label": "%", "value": "1"},
                ],
                value="0",
            ),
            dbc.Row(
                [
                    dbc.Col(html.Div(national_map)),
                    dbc.Col(html.Div(national_plot)),
                ],
            ),
            dcc.Store(id="store-national", storage_type="memory", data=make_plots()),
            dcc.Store(
                id="store-map-national",
                storage_type="memory",
                data=make_map_plot(boundaries=boundaries),
            ),
            dcc.Store(id="store-gsp-boundaries", storage_type="memory", data=boundaries),
        ],
        style={"height": "95vh"},
    )

    return tab1
