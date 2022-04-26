from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

import logging

from auth import make_auth
from plots import make_plot, make_map_plot
from callbacks import make_callbacks


logger = logging.getLogger(__name__)
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


"""Construct core Flask application with embedded Dash app."""


# Import Dash application
def make_app():
    app = Dash(
        __name__,
        external_stylesheets=external_stylesheets + [dbc.themes.BOOTSTRAP],
        url_base_pathname="/dash/",
    )

    make_auth(app)

    modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader("GSP plot"),
                    dbc.ModalBody(
                        [
                            html.H4(id="hover_info"),
                            dcc.Graph(
                                id="plot-modal",
                                figure=make_plot(gsp_id=1, show_yesterday=False)
                            ),
                        ]
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close", className="ml-auto")),
                    dcc.Store(id='store-gsp', storage_type='memory'),
                ],
                id="modal",
                is_open=False,
                style={"width": "50%"},
            ),
        ]
    )

    tab1 = html.Div(
        [
            html.H3(f"Summary"),
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
            dcc.Graph(
                id="plot-national",
                figure=make_plot(gsp_id=0, show_yesterday=False)
            ),
            dcc.Store(id='store-national', storage_type='memory'),
        ]
    )

    app.layout = html.Div(children=[html.H1(children="Data visualization dashboard"), tab1])

    app = make_callbacks(app)

    return app


if __name__ == "__main__":
    app = make_app()
    app.run_server(debug=True, port=3000)
