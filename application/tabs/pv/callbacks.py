""" Callbacks functions """
from typing import List

import numpy as np
from dash import Input, Output, State

from .plots import make_pv_plot


def pv_make_callbacks(app):
    """Make callbacks"""

    @app.callback(
        Output("pv-plot", "figure"),
        Input("pv-dropdown", "value"),
    )
    def update_pv_plot(pv_system_id: List[int]):
        print(f"Updating PV plot with pv system {pv_system_id}")
        fig = make_pv_plot(pv_systems_ids=pv_system_id)
        print(f"Updating PV plot: done")
        return fig

    @app.callback(
        Output("pv-dropdown", "value"),
        Input("pv-random", "n_clicks"),
        State('store-pv-system-id','data')
    )
    def make_random_pv_systems_ids(n_clicks, all_pv_systems_ids):

        random_choices = list(np.random.choice(len(all_pv_systems_ids), 10))
        init_pv_systems = np.array(all_pv_systems_ids)[random_choices]

        print(f"random chooses are {init_pv_systems}")

        return init_pv_systems

    return app
