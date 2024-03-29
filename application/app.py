""" Main app file """

import asyncio
import os

import dash_bootstrap_components as dbc
import psutil
from auth import make_auth
from dash import Dash, dcc, html
from log import logger
from tabs.nwp.callbacks import nwp_make_callbacks
from tabs.nwp.layout import nwp_make_layout
from tabs.pv.callbacks import pv_make_callbacks
from tabs.pv.layout import pv_make_layout
from tabs.satellite.callbacks import satellite_make_callbacks
from tabs.satellite.layout import satellite_make_layout
from tabs.status.callbacks import make_status_callbacks
from tabs.status.layout import make_status_layout
from tabs.summary.callbacks import make_callbacks
from tabs.summary.layout import make_layout

# logging.getLogger("app").setLevel('DEBUG')
# logger.setLevel(getattr(logging, os.environ.get("LOG_LEVEL", "DEBUG")))
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

version = "1.0.4"
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
        tasks.append(asyncio.create_task(satellite_make_layout()))
        tasks.append(asyncio.create_task(make_layout()))
        tasks.append(asyncio.create_task(pv_make_layout()))
        tasks.append(asyncio.create_task(make_status_layout()))
        tasks.append(asyncio.create_task(nwp_make_layout()))
        res = await asyncio.gather(*tasks)
        return res

    use_async = False
    if use_async:

        (
            tab_sat,
            tab_summary,
            tab_pv,
            tab_status,
            tab_nwp,
        ) = asyncio.get_event_loop().run_until_complete(make_all_tabs_layout())
    else:
        logger.debug("Adding tabs")
        try:
            logger.debug("Adding Satellite tab")
            tab_sat = asyncio.run(satellite_make_layout())
        except Exception as e:
            logger.error(e)
            logger.debug("Could not make satellite tab")
            tab_sat = None

        try:
            logger.debug("Adding Summary tab")
            tab_summary = asyncio.run(make_layout())
        except Exception as e:
            logger.error(e)
            logger.debug("Could not make summary tab")
            tab_summary = None

        try:
            logger.debug("Adding PV tab")
            tab_pv = asyncio.run(pv_make_layout())
        except Exception as e:
            logger.error(e)
            logger.debug("Could not make pv tab")
            tab_pv = None

        try:
            logger.debug("Adding Status tab")
            tab_status = asyncio.run(make_status_layout())
        except Exception as e:
            logger.error(e)
            logger.debug("Could not make status tab")
            tab_status = None

        try:
            logger.debug("Adding NWP tab")
            tab_nwp = asyncio.run(nwp_make_layout())
        except Exception as e:
            logger.error(e)
            logger.debug("Could not make nwp tab")
            tab_nwp = None

    logger.debug("Done adding tabs")

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
                    dcc.Tab(tab_nwp, label="NWP", value="tab-nwp"),
                    dcc.Tab(tab_sat, label="Satellite", value="tab-sat"),
                ],
            ),
            html.Div(id="tabs-content-example-graph"),
            html.Footer(f"version {version}", id="footer"),
        ]
    )

    # add other tab callbacks
    logger.debug("Adding Callbacks")
    app = make_callbacks(app)
    app = pv_make_callbacks(app)
    app = make_status_callbacks(app)
    app = nwp_make_callbacks(app)
    app = satellite_make_callbacks(app)
    logger.debug("Done adding Callbacks")

    # print memoery
    process = psutil.Process(os.getpid())
    logger.debug(f"Memory is {process.memory_info().rss / 10 ** 6} MB")

    return app


if __name__ == "__main__":
    app = make_app()
    app.run_server(debug=True, port=8000, host="0.0.0.0")
