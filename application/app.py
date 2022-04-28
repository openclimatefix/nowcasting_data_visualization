""" Main app file """
import logging

import dash_bootstrap_components as dbc
from auth import make_auth
from dash import Dash, dcc, html
from dash import Input, Output

from tabs.summary.callbacks import make_callbacks
from tabs.summary.layout import make_layout

logger = logging.getLogger(__name__)
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

version = "0.0.6"


"""Construct core Flask application with embedded Dash app."""


# Import Dash application
def make_app():
    """Make Dash App"""
    app = Dash(
        __name__,
        external_stylesheets=external_stylesheets + [dbc.themes.BOOTSTRAP],
        url_base_pathname="/dash/",
    )

    make_auth(app)

    tab1 = make_layout()

    app.layout = html.Div(
        children=[
            html.H1(children="Data visualization dashboard"),
            dcc.Tabs(
                id="tabs-example-graph",
                value="tab-1",
                children=[
                    dcc.Tab(label="Summary", value="tab-1"),
                    dcc.Tab(label="PV", value="tab-2"),
                ],
            ),
            html.Div(id="tabs-content-example-graph"),
            html.Footer(f"version {version}", id="footer"),
        ]
    )

    # call back to switch tabs
    @app.callback(
        Output("tabs-content-example-graph", "children"), Input("tabs-example-graph", "value")
    )
    def render_content(tab):
        if tab == "tab-1":
            return tab1
        elif tab == "tab-2":
            return html.H2(children="PV data")

    # add other tab callbacks
    app = make_callbacks(app)

    return app


if __name__ == "__main__":
    app = make_app()
    app.run_server(debug=True, port=8000, host="0.0.0.0")

