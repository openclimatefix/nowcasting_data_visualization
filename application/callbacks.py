from dash import Output, Input, State

from typing import List

from plots import make_plot


def make_callbacks(app):
    @app.callback(
        [Output("gsp-output-container", "children"), Output("plot-gsp", "figure")],
        [Input("gsp-dropdown", "value")],
    )
    def update_output(gsp_value: str):
        print(f"Updating GSP value {gsp_value}")
        fig = make_plot(gsp_id=int(gsp_value), show_yesterday=True)
        return f"You have selected {gsp_value}", fig

    @app.callback(
        Output("plot-national", "figure"),
        Input("tick-show-yesterday", "value"),
        State('store-national','data')
    )
    def update_national_output(yesterday_value: List[str], store_national_data):
        print(f"Updating National plot, {yesterday_value=}")
        show_yesterday = True if "Yesterday" in yesterday_value else False
        fig = make_plot(gsp_id=0, show_yesterday=show_yesterday)
        return fig

    @app.callback(
        [Output("modal", "is_open"), Output("plot-modal", "figure")],
        [Input("plot-uk", "clickData"), Input("close", "n_clicks")],
        [State("modal", "is_open"), State("plot-modal", "figure")],
    )
    def toggle_modal(click_data, close_button, is_open, fig):

        print(f"{click_data=} {close_button=} {is_open=}")

        if (close_button is None) and (click_data is None) and (fig is not None):
            print('Sometimes this callback gets triggered with no data, '
                  'but the figure is already there')
            return is_open, fig

        if click_data or close_button:
            new_is_open = not is_open
            print(f"Modal open/close from {is_open} to {new_is_open}")
        else:
            new_is_open = is_open

        if click_data is not None:

            print("Making plot")
            gsp_id = int(click_data["points"][0]["pointNumber"] + 1)
            fig = make_plot(gsp_id=gsp_id, show_yesterday=False)
        else:
            print("Not making plot, probably because we are closing the window down")
            fig = None

        return new_is_open, fig

    return app
