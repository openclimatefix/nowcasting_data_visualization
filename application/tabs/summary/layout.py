""" Make summary layout """
import logging

import dash_bootstrap_components as dbc
from dash import dcc, html

from .plots import make_map_plot, make_plot

logger = logging.getLogger(__name__)


def make_layout():
    """Make Summary layout"""
    modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader("GSP plot"),
                    dbc.ModalBody(
                        [
                            html.H4(id="hover_info"),
                            dcc.Graph(
                                id="plot-modal", figure=make_plot(gsp_id=1, show_yesterday=False)
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
                figure=make_plot(gsp_id=0, show_yesterday=False),
            ),
        ],
        style={"width": "95%"},
    )

    national_map = html.Div(
        [
            dcc.Graph(
                id="plot-uk",
                figure=make_map_plot(),
            ),
            modal,
        ],
        style={"width": "95%"},
    )

    tab1 = html.Div(
        children=[
            # html.H3("Summary"),
            dcc.RadioItems(
                id="radio-gsp-pv",
                options=[
                    {"label": "GSP Forecast", "value": "Forecast"},
                    {"label": "PVLive", "value": "PVLive"},
                ],
                value="Forecast",
            ),
            dbc.Row(
                [
                    dbc.Col(html.Div(national_map)),
                    dbc.Col(html.Div(national_plot)),
                ],
            ),
            dcc.Store(id="store-national", storage_type="memory"),
        ],
        style={"height": "95vh"},
    )

    return tab1
