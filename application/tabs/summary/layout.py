import logging

import dash_bootstrap_components as dbc
from dash import dcc, html

from .plots import make_map_plot, make_plot

logger = logging.getLogger(__name__)


def make_layout():

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
                style={"width": "50%"},
            ),
        ]
    )

    tab1 = html.Div(
        [
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
                    dcc.Graph(
                        id="plot-uk",
                        figure=make_map_plot(),
                        style={"width": "90%"},
                    ),
                    modal,
                ]
            ),
            dcc.Checklist(["Yesterday"], [""], id="tick-show-yesterday"),
            dcc.Graph(id="plot-national", figure=make_plot(gsp_id=0, show_yesterday=False)),
            dcc.Store(id="store-national", storage_type="memory"),
        ]
    )

    return tab1
