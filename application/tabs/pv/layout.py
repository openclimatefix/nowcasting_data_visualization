""" PV lyaout code """
import logging

import dash_bootstrap_components as dbc
import numpy as np
from dash import dcc, html

from .plots import get_all_pv_systems_ids, make_pv_plot

logger = logging.getLogger(__name__)


def pv_make_layout():
    """ Make pv htm layout """

    all_pv_systems_ids = get_all_pv_systems_ids()
    random_choices = list(np.random.choice(len(get_all_pv_systems_ids()), 10))
    init_pv_systems = np.array(all_pv_systems_ids)[random_choices]

    tab2 = html.Div(
        [
            html.H3("PV data from today"),
            dcc.Dropdown(
                all_pv_systems_ids,
                init_pv_systems,
                id="pv-dropdown",
                style={"width": "50%"},
                multi=True,
            ),
            dbc.Button("Random", id="pv-random"),
            dcc.Graph(
                id="pv-plot",
                figure=make_pv_plot(),
                style={"width": "50%"},
            ),
            dcc.Store(id="store-pv-system-id",
                      storage_type="memory",
                      data=all_pv_systems_ids),
        ]
    )

    return tab2
