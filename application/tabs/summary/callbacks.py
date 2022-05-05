""" Callbacks functions """
from datetime import datetime, timezone
from typing import List

from dash import Input, Output, State
from log import logger

from .plots import make_map_plot, make_plots


def make_callbacks(app):
    """Make callbacks"""

    # refresh map
    @app.callback(
        Output("plot-map", "figure"),
        Input("summary-slider-update", "n_intervals"),
        State("store-map-national", "data"),
    )
    def refresh_map(n_intervals_slider, figs):

        logger.debug(f"Refreshing summary map, {n_intervals_slider=}")

        N = len(figs)
        if n_intervals_slider is None:
            i = 0
        else:
            i = n_intervals_slider % N

        fig = figs[i]

        logger.debug(f"Refreshing summary map: done")

        return fig

    # refresh data and national plot
    @app.callback(
        [
            Output("store-national", "data"),
            Output("store-map-national", "data"),
            Output("summary-refresh-status", "children"),
        ],
        [Input("summary-refresh", "n_clicks"), Input("summary-interval", "n_intervals")],
        State("store-gsp-boundaries", "data"),
    )
    def refresh_trigger(n_clicks, n_intervals, boundaries):

        logger.debug(f"Refreshing Summary data {n_clicks=} {n_intervals=}")

        national = make_plots()
        national_map = make_map_plot(boundaries=boundaries)

        now_text = datetime.now(timezone.utc).strftime("Refresh time: %Y-%m-%d %H:%M:%S  [UTC]")
        return national, national_map, f"Last refreshed at {now_text}"

    @app.callback(
        Output("plot-national", "figure"),
        [Input("tick-show-yesterday", "value"), Input("store-national", "data")],
    )
    def update_national_output(yesterday_value: List[str], store_national_data):
        print(f"Updating National plot, {yesterday_value=}")
        show_yesterday = 0 if "Yesterday" in yesterday_value else 1
        fig = store_national_data[show_yesterday]
        return fig

    @app.callback(
        [Output("modal", "is_open"), Output("plot-modal", "figure")],
        [Input("plot-map", "clickData"), Input("close", "n_clicks")],
        [State("modal", "is_open"), State("plot-modal", "figure")],
    )
    def toggle_modal(click_data, close_button, is_open, fig):
        """Call back for pop up GSP graph"""
        return toggle_modal_function(click_data, close_button, is_open, fig)

    return app


def toggle_modal_function(click_data, close_button, is_open, fig):
    """Function to toggle gsp graph on or off"""
    print(f"{click_data=} {close_button=} {is_open=}")

    if (close_button is None) and (click_data is None) and (fig is not None):
        print(
            "Sometimes this callback gets triggered with no data, "
            "but the figure is already there"
        )
        return is_open, fig

    if click_data or close_button:
        new_is_open = not is_open
        print(f"Modal open/close from {is_open} to {new_is_open}")
    else:
        new_is_open = is_open

    if click_data is not None:

        print("Making plot")
        gsp_id = int(click_data["points"][0]["pointNumber"] + 1)
        fig = make_plots(gsp_id=gsp_id, show_yesterday=False)
    else:
        print("Not making plot, probably because we are closing the window down")
        fig = None

    return new_is_open, fig
