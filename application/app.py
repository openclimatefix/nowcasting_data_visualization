""" Main app file """

import dash_bootstrap_components as dbc
from auth import make_auth
from dash import Dash, dcc, html
from log import logger
from tabs.nwp.callbacks import nwp_make_callbacks
from tabs.nwp.layout import nwp_make_layout
from tabs.pv.callbacks import pv_make_callbacks
from tabs.pv.layout import pv_make_layout
from tabs.status.callbacks import make_status_callbacks
from tabs.status.layout import make_status_layout
from tabs.summary.callbacks import make_callbacks
from tabs.summary.layout import make_layout
import asyncio

# logging.getLogger("app").setLevel('DEBUG')
# logger.setLevel(getattr(logging, os.environ.get("LOG_LEVEL", "DEBUG")))
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

version = "0.0.36"
logger.debug(f"Running {version} of Data visulization ")
print(version)


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

    async def make_all_tabs_layout():
        tasks = []
        tasks.append(asyncio.create_task(make_layout()))
        tasks.append(asyncio.create_task(pv_make_layout()))
        tasks.append(asyncio.create_task(make_status_layout()))
        res = await asyncio.gather(*tasks)
        return res

    tab_summary, tab_pv, tab_status = asyncio.get_event_loop().run_until_complete(make_all_tabs_layout())


    # TODO make async to speed up
    # tab_summary = results["summary"]
    # tab_pv = results["pv"]
    # tab_status = results["status"]
    # tab_nwp = results["nwp"]

    app.layout = html.Div(
        children=[
            html.H1(children="Data visualization dashboard"),
            dcc.Tabs(
                id="tabs-example-graph",
                value="tab-status",
                children=[
                    dcc.Tab(tab_summary, label="Summary", value="tab-summary"),
                    dcc.Tab(tab_status, label="Status", value="tab-status"),
                    dcc.Tab(tab_pv, label="PV", value="tab-pv"),
                    # dcc.Tab(tab_nwp, label="NWP", value="tab-nwp"),
                ],
            ),
            # html.Div(id="tabs-content-example-graph"),
            html.Footer(f"version {version}", id="footer"),
        ]
    )

    # add other tab callbacks
    app = make_callbacks(app)
    app = pv_make_callbacks(app)
    app = make_status_callbacks(app)
    app = nwp_make_callbacks(app)

    return app


if __name__ == "__main__":
    app = make_app()
    app.run_server(debug=True, port=8000, host="0.0.0.0")
