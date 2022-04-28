""" Main app file """
import logging

import dash_bootstrap_components as dbc
from auth import make_auth
from dash import Dash, Input, Output, dcc, html
from tabs.pv.callbacks import pv_make_callbacks
from tabs.pv.layout import pv_make_layout
from tabs.summary.callbacks import make_callbacks
from tabs.summary.layout import make_layout

logger = logging.getLogger(__name__)
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

version = "0.0.8"


"""Construct core Flask application with embedded Dash app."""


# Import Dash application
def make_app():
    """Make Dash App"""
    app = Dash(
        __name__,
        external_stylesheets=external_stylesheets + [dbc.themes.BOOTSTRAP],
        # url_base_pathname="/dash/",
    )

    make_auth(app)

    tab1 = make_layout()
    tab2 = pv_make_layout()

    app.layout = html.Div(
        children=[
            html.H1(children="Data visualization dashboard"),
            dcc.Tabs(
                id="tabs-example-graph",
                value="tab-2",
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
            print("Making tab1")
            layout = tab1
        elif tab == "tab-2":
            print("Making tab2")
            layout = tab2
        return layout

    # add other tab callbacks
    app = make_callbacks(app)
    app = pv_make_callbacks(app)

    return app


if __name__ == "__main__":
    app = make_app()
    app.run_server(debug=True, port=8000, host="0.0.0.0")
