""" Callbacks functions """
from datetime import datetime, timezone
from typing import List

from dash import Input, Output, State
from log import logger

from .plots import make_map_plot, make_plots, gat_map_data


def make_callbacks(app):
    """Make callbacks"""

    app.clientside_callback(
        """
        function(n_intervals, normalize, data) {
            let N = data.length
            let n_index = parseInt(normalize)
            i = n_intervals % N
            console.log(i,n_index)
            return data[n_index][i]
            }
        """,
        Output("plot-map", "figure"),
        [Input("summary-slider-update", "n_intervals"),Input("radio-summary-normalize", "value")],
        State("store-map-national", "data"),
    )

    # refresh data and national plot
    @app.callback(
        [
            Output("store-national", "data"),
            Output("store-summary-plot-map-data", "data"),
            Output("summary-refresh-status", "children"),
        ],
        [
            Input("summary-refresh", "n_clicks"),
            Input("summary-interval", "n_intervals"),
        ],
        State("store-gsp-boundaries", "data"),
    )
    def refresh_trigger(n_clicks, n_intervals, boundaries):

        logger.debug(f"Refreshing Summary data {n_clicks=} {n_intervals=}")

        national = make_plots()
        national_map = gat_map_data(boundaries=boundaries)

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

    @app.callback(
        Output("store-map-national", "data"),
        Input("store-summary-plot-map-data", "data"),
        State("store-gsp-boundaries", "data"),
    )
    def callback_make_map_plot(map_data,normalize, boundaries):

        logger.debug(f'Making map plot from map data and {normalize=}')
        normalize = bool(int(normalize))

        return make_map_plot(boundaries=boundaries,d=map_data)

    return app
