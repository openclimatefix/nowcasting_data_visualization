""" Callbacks functions """
from datetime import datetime, timezone
from typing import List

from dash import Input, Output, State
from log import logger

from .plots import make_map_plot, make_plots


def make_callbacks(app):
    """Make callbacks"""

    app.clientside_callback(
        """
        function(n_intervals, data) {
            let N = data.length
            i = n_intervals % N
            return data[i]
            }
        """,
        Output("plot-map", "figure"),
        Input("summary-slider-update", "n_intervals"),
        State("store-map-national", "data"),
    )

    # refresh data and national plot
    @app.callback(
        [
            Output("store-national", "data"),
            Output("store-map-national", "data"),
            Output("summary-refresh-status", "children"),
        ],
        [
            Input("summary-refresh", "n_clicks"),
            Input("summary-interval", "n_intervals"),
            Input("radio-summary-normalize", "value"),
        ],
        State("store-gsp-boundaries", "data"),
    )
    def refresh_trigger(n_clicks, n_intervals, normalize: bool, boundaries):

        logger.debug(f"Refreshing Summary data {n_clicks=} {n_intervals=} {normalize=}")
        normalize = bool(int(normalize))

        national = make_plots()
        national_map = make_map_plot(boundaries=boundaries, normalize=normalize)

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
        Output("plot-modal", "figure"),
        Input("plot-map", "clickData"),
    )
    def toggle_modal(click_data):
        """Call back for pop up GSP graph"""

        gsp_id = int(click_data["points"][0]["pointNumber"] + 1)
        fig = make_plots(gsp_id=gsp_id, show_yesterday=False)

        return fig

    return app
